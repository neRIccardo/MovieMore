from django.http import Http404
from django.shortcuts import redirect, render
from django.utils import timezone
from screenings.forms import ScreeningsSearchForm
from screenings.models import Screening
from movies.forms import *
from django.db.models import Sum
from django.views.generic import ListView
from django.views.generic.edit import UpdateView, CreateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import AccessMixin
from django.views.generic import TemplateView

# Funzione per verificare che un utente sia nel gruppo degli amministratori
def is_cinema_admin(user):
    return user.groups.filter(name='AmministratoriCinema').exists()

# Classe per gestire le autorizzazioni
class CustomRequired(AccessMixin):

    def dispatch(self, request, *args, **kwargs): # Metodo che gestisce la logica di inizializzazione della vista e il controllo preliminare
        if not request.user.is_authenticated:
            return not_authorized(request)

        user_groups = request.user.groups.values_list('name', flat=True)
        if not self.group_required == None:
            if not set(self.group_required).intersection(set(user_groups)):
                return not_authorized(request)

        return super().dispatch(request, *args, **kwargs)

# Function view per renderizzare la home
def cinema_home(request):
    is_admin_cinema = is_cinema_admin(request.user)
    return render(request, 'home.html', {'is_admin_cinema': is_admin_cinema})

# Class based view per renderizzare la programmazione
class CinemaSchedulingView(ListView):
    model = Screening
    template_name = 'scheduling.html'
    paginate_by = 3

    def get_context_data(self, **kwargs): # Metodo che aggiunge dati aggiuntivi al contesto del template
        context = super().get_context_data(**kwargs)
        is_admin_cinema = is_cinema_admin(self.request.user)
        today = timezone.now().date()
        days = [(today + timezone.timedelta(days=offset)).strftime('%d-%m-%Y') for offset in range(7)]
        selected_day = self.request.GET.get('selected_day', today.strftime('%d-%m-%Y'))

        screenings_by_day = {}
        for day in days:
            day_date = timezone.datetime.strptime(day, '%d-%m-%Y').date()
            screenings_by_day[day] = Screening.objects.filter(start_time__date=day_date)
        
        selected_screenings = screenings_by_day.get(selected_day, [])

        context.update({
            'days': days,
            'selected_day': selected_day,
            'is_admin_cinema': is_admin_cinema,
            'screening': selected_screenings
        })
        return context

    def get_queryset(self): # Metodo che restituisce la queryset delle proiezioni da visualizzare
        selected_day = self.request.GET.get('selected_day', timezone.now().date().strftime('%d-%m-%Y'))
        day_date = timezone.datetime.strptime(selected_day, '%d-%m-%Y').date()
        queryset = Screening.objects.filter(start_time__date=day_date)
        
        for screening in queryset:
            screening.remaining_seats = screening.room.capacity - (screening.bookings.aggregate(Sum('seats'))['seats__sum'] or 0)
        
        return queryset

# Class based view per la renderizzazione della collezione
class CinemaCollectionView(ListView):
    model = Screening
    template_name = 'collection.html'
    context_object_name = 'screenings'
    paginate_by = 10

    def get_context_data(self, **kwargs): # Metodo che aggiunge dati aggiuntivi al contesto del template
        context = super().get_context_data(**kwargs)
        context['form'] = self.form
        context['searched'] = self.searched
        context['is_admin_cinema'] = self.is_admin_cinema
        return context

    def get_queryset(self): # Metodo che restituisce la queryset delle proiezioni da visualizzare
        self.form = ScreeningsSearchForm(self.request.GET or None)
        screenings = Screening.objects.all()
        self.searched = False
        self.is_admin_cinema = is_cinema_admin(self.request.user)

        if self.form.is_valid():
            title = self.form.cleaned_data.get('title')
            genre = self.form.cleaned_data.get('genre')
            start_date = self.form.cleaned_data.get('start_date')
            end_date = self.form.cleaned_data.get('end_date')
            order_by = self.form.cleaned_data.get('order_by')
            self.searched = True

            if title:
                screenings = screenings.filter(movie__title__icontains=title)
            if genre:
                screenings = screenings.filter(movie__genre__icontains=genre)
            if start_date and end_date:
                if start_date == end_date:
                    screenings = screenings.filter(start_time__date=start_date)
                else:
                    screenings = screenings.filter(start_time__date__range=(start_date, end_date))
            elif start_date:
                screenings = screenings.filter(start_time__date__gte=start_date)
            elif end_date:
                screenings = screenings.filter(start_time__date__lte=end_date)

            if order_by:
                screenings = screenings.order_by(order_by)
            else:
                screenings = screenings.order_by('start_time')

        for screening in screenings:
            remaining_seats = screening.room.capacity - (screening.bookings.aggregate(Sum('seats'))['seats__sum'] or 0)
            screening.remaining_seats = remaining_seats

        return screenings

# Class based view per renderizzare il pannello degli amministratori
class ManagementPanelView(CustomRequired, TemplateView):
    template_name = "management_panel.html"
    group_required = ["AmministratoriCinema"]

# Funzione per renderizzare la pagina 404
def custom_404_view(request):
    return render(request, '404.html', status=404)

# Funzione per renderizzare la pagina 403
def not_authorized(request):
    return render(request, 'not_authorized.html', status=403)

# Class based view per renderizzare i template relativi all'aggiunta di oggetti
class AddItemView(CustomRequired, CreateView):
    template_name = ''
    success_url = reverse_lazy('management')
    success_message = ''
    group_required = ['AmministratoriCinema']

    def form_valid(self, form): # Metodo chiamato quando i dati del form sono validi
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response

# Class based view per renderizzare i template relativi la modifica di oggetti
class EditItemView(CustomRequired, UpdateView):
    template_name = ''
    success_url = reverse_lazy('management')
    success_message = ''
    group_required = ['AmministratoriCinema']

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response
    
    def dispatch(self, *args, **kwargs): # Metodo che gestisce la logica di inizializzazione della vista e il controllo preliminare
        try:
            return super().dispatch(*args, **kwargs)
        except Http404:
            return custom_404_view(self.request)

# Class based view per renderizzare i template relativi alla rimozione di oggetti
class DeleteItemView(CustomRequired, DeleteView):
    template_name = ''
    success_url = reverse_lazy('management')
    success_message = ''
    group_required = ['AmministratoriCinema']

    def post(self, *args, **kwargs):
        obj = self.get_object()
        obj.delete()
        messages.success(self.request, self.success_message)
        return redirect(self.success_url)
    
    def dispatch(self, *args, **kwargs): # Metodo che gestisce la logica di inizializzazione della vista e il controllo preliminare
        try:
            return super().dispatch(*args, **kwargs)
        except Http404:
            return custom_404_view(self.request)