from django import forms
from .models import *
import re
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum
from bookings.models import *

# Forma per l'aggiunta/modifica di una sala
class ScreeningRoomForm(forms.ModelForm):
    class Meta:
        model = ScreeningRoom
        fields = '__all__'
        labels = {
            'name': 'Nome della sala',
            'capacity': 'Capacità'
        }
    
    def __init__(self, *args, **kwargs):
        super(ScreeningRoomForm, self).__init__(*args, **kwargs)
        self.original_name = self.instance.name if self.instance.pk else None

    def clean_name(self): # Metodo per controllare il nome
        name = self.cleaned_data.get('name')
        if self.instance.pk and name == self.original_name:
            return name
        if ScreeningRoom.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError("Una sala con lo stesso nome è già presente nel database.")
        if not re.match(r'^Sala\s\d+$', name):
            raise forms.ValidationError("Nome non nel formato valido")
        return name

    def clean_capacity(self): # Metodo per controllare la capacità
        capacity = self.cleaned_data.get('capacity')
        if capacity <= 0:
            raise forms.ValidationError("La capacità deve essere un numero positivo")

        # Controlla se ci sono prenotazioni per le proiezioni in questa sala
        if self.instance.pk:  # Solo se la sala esiste già
            # Ottieni tutte le proiezioni nella sala
            screenings = Screening.objects.filter(room=self.instance)

            # Trova il massimo totale di posti prenotati tra tutte le proiezioni nella sala
            max_total_booked_seats = 0
            for screening in screenings:
                total_booked_seats = Booking.objects.filter(screening=screening).aggregate(total=Sum('seats'))['total']
                if total_booked_seats is not None:
                    if total_booked_seats > max_total_booked_seats:
                        max_total_booked_seats = total_booked_seats

            if max_total_booked_seats > 0 and capacity < max_total_booked_seats:
                raise forms.ValidationError(f"La capacità non può essere inferiore al numero massimo di posti già prenotati per una proiezione ({max_total_booked_seats}).")

        return capacity

# Form per l'aggiunta/modifica di una proiezione
class ScreeningForm(forms.ModelForm):
    class Meta:
        model = Screening
        fields = '__all__'
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
        labels = {
            'movie': 'Titolo del film',
            'room': 'Sala del cinema',
            'start_time': 'Giorno ed orario di inizio',
            'price': 'Prezzo del biglietto',
        }

    
    # filtra le proiezioni nel database che si trovano nella stessa sala (room_id) e il cui orario di
    # inizio è prima dell'orario di fine della nuova proiezione, e il cui orario di fine è
    # dopo l'orario di inizio della nuova proiezione. Inoltre verifica se la nuova proiezione
    # è completamente inclusa all'interno della proiezione esistente.
    # Questo criterio assicura che qualsiasi sovrapposizione venga rilevata
    def is_overlapping(self, room_id, start_time, movie_duration, screening_id=None):
        end_time = start_time + timedelta(minutes=movie_duration)
        screenings = Screening.objects.filter(room_id=room_id)
        
        # Se stiamo modificando una proiezione esistente la escludiamo dai controlli
        if screening_id:
            screenings = screenings.exclude(id=screening_id)
        
        for screening in screenings:
            existing_start_time = screening.start_time
            existing_end_time = screening.start_time + timedelta(minutes=screening.movie.duration)
            
            # Controlla sovrapposizioni
            if (start_time < existing_end_time and end_time > existing_start_time) or \
               (start_time >= existing_start_time and end_time <= existing_end_time):
                return True
        
        return False

    def clean_start_time(self): # Metodo per controllare la data/orario della proiezione
        start_time = self.cleaned_data.get('start_time')
        room = self.cleaned_data.get('room')
        movie = self.cleaned_data.get('movie')
        
        if start_time and room and movie:
            movie_duration = movie.duration
            screening_id = self.instance.id if self.instance else None

            if self.is_overlapping(room.id, start_time, movie_duration, screening_id):
                raise forms.ValidationError('La nuova proiezione si sovrappone con una proiezione esistente.')
        
        if start_time < timezone.now():
            raise forms.ValidationError("La data e l'orario di inizio non possono essere precedenti a quelli attuali.")
        
        return start_time

    def clean_price(self): # Metodo per controllare il prezzo
        price = self.cleaned_data.get('price')
        if price is not None and price <= 0:
            raise forms.ValidationError('Il prezzo deve essere maggiore di zero.')
        return price

# Form per la ricerca delle proiezioni
class ScreeningsSearchForm(forms.Form):
    title = forms.CharField(max_length=255, required=False, label='Titolo')
    genre = forms.CharField(max_length=50, required=False, label='Genere')
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}), label='Data di inizio proiezione')
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}), label='Data di fine proiezione')
    order_by = forms.ChoiceField(
        required=False,
        choices=[
            ('movie__title', 'titolo (A-Z)'),
            ('-movie__title', 'titolo (Z-A)'),
            ('start_time', 'data (Crescente)'),
            ('-start_time', 'data (Decrescente)'),
            ('start_time__time', 'orario (Crescente)'),
            ('-start_time__time', 'orario (Decrescente)'),
        ],
        label='Ordina per'
    )

    labels = {
            'title': 'Totolo',
            'genre': 'Genere',
            'start_date': 'Data di partenza',
            'end_date': 'Data di fine'
        }