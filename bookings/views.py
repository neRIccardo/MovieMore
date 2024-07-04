import random
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Screening
from .forms import BookingForm
from django.db.models import Sum
from django.views.generic import CreateView
from .models import Screening, Booking
from django.urls import reverse_lazy
from cinema.views import custom_404_view, CustomRequired

# Funzione per generare i numeri di posto in base a quanti posti ha acquistato l'utente
def generate_seat_numbers(screening, num_seats):
    total_seats = list(range(1, screening.room.capacity + 1))
    booked_seats = screening.bookings.values_list('seat_numbers', flat=True)
    booked_seats = [int(seat) for sublist in booked_seats for seat in sublist.split(',')]
    available_seats = list(set(total_seats) - set(booked_seats))

    if num_seats > len(available_seats):
        raise ValueError("Non ci sono abbastanza posti disponibili.")

    return random.sample(available_seats, num_seats)

# Vista per l'acquisto di una proiezione
class PurchaseTicketsView(CustomRequired, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'purchase_ticket.html'
    group_required = None
    
    def dispatch(self, *args, **kwargs): # Metodo che gestisce la logica di inizializzazione della vista e il controllo preliminare
        try:
            self.screening = get_object_or_404(Screening, id=self.kwargs['screening_id'])
        except Http404:
            return custom_404_view(self.request)
        
        total_booked_seats = self.screening.bookings.aggregate(total=Sum('seats'))['total'] or 0
        if total_booked_seats >= self.screening.room.capacity:
            messages.success(self.request, 'Proiezione sold out.')
            return redirect('home')
        return super().dispatch(*args, **kwargs)

    def get_initial(self): #  Metodo che restituisce i dati iniziali per il form
        user = self.request.user
        initial = super().get_initial()
        initial.update({
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
        })
        return initial

    def get_context_data(self, **kwargs): # Metodo che aggiunge dati aggiuntivi al contesto del template
        context = super().get_context_data(**kwargs)
        total_booked_seats = self.screening.bookings.aggregate(total=Sum('seats'))['total'] or 0
        available_seats = self.screening.room.capacity - total_booked_seats
        context.update({
            'screening': self.screening,
            'available_seats': available_seats,
        })
        return context

    def form_valid(self, form): # Metodo chiamato quando i dati del form sono validi
        user = self.request.user
        form.instance.user = user
        form.instance.screening = self.screening

        total_booked_seats = self.screening.bookings.aggregate(total=Sum('seats'))['total'] or 0
        requested_seats = form.cleaned_data['seats']
        if requested_seats <= (self.screening.room.capacity - total_booked_seats):
            seat_numbers = generate_seat_numbers(self.screening, requested_seats)
            seat_numbers_str = ','.join(map(str, seat_numbers))  # conversione della lista di numeri in una stringa separata da virgole
            form.instance.seat_numbers = seat_numbers_str
            messages.success(self.request, 'Prenotazione effettuata con successo.')
            return super().form_valid(form)
        else:
            form.add_error('seats', 'Numero di posti richiesti non disponibile.')
            return self.form_invalid(form)

    def get_success_url(self): # Metodo che restituisce l'URL di reindirizzamento dopo il completamento con successo dell'operazione di acquisto
        return reverse_lazy('home')