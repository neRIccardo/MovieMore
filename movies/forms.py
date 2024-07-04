from django import forms

from screenings.models import Screening
from .models import Movie
import re
from datetime import datetime, timedelta

class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = '__all__'
        labels = {
            'title': 'Titolo',
            'description': 'Descrizione',
            'poster': 'Locandina',
            'release_date': 'Data di uscita',
            'cast': 'Cast',
            'duration': 'Durata',
            'genre': 'Genere',
            'director': 'Regista',
        }

    def __init__(self, *args, **kwargs):
        super(MovieForm, self).__init__(*args, **kwargs)
        self.original_title = self.instance.title if self.instance.pk else None
        self.original_duration = self.instance.duration if self.instance.pk else None

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if self.instance.pk and title == self.original_title:
            return title
        if Movie.objects.filter(title__iexact=title).exists():
            raise forms.ValidationError("Un film con lo stesso titolo è già presente nel database.")
        return title
    
    def clean_release_date(self):
        release_date = self.cleaned_data.get('release_date')
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', str(release_date)):
            raise forms.ValidationError("Il formato della data non è corretto. Utilizza il formato aaaa-mm-gg.")
        if release_date > datetime.now().date():
            raise forms.ValidationError("La data di uscita non può essere maggiore della data odierna.")
        return release_date

    def clean_director(self):
        director = self.cleaned_data.get('director')
        if any(char.isdigit() for char in director) or not re.match(r'^(\s*\b[a-zA-Z]+\b\s*)+$', director):
            raise forms.ValidationError("Regista non nel formato corretto")
        return director
    
    def clean_genre(self):
        genre = self.cleaned_data.get('genre')
        if any(char.isdigit() for char in genre) or not re.match(r'^[A-Za-z]+(?:,\s[A-Za-z]+)*$', genre):
            raise forms.ValidationError("Genere non nel formato corretto")
        return genre

    def clean_cast(self):
        cast = self.cleaned_data.get('cast')
        if any(char.isdigit() for char in cast) or not re.match(r'^(\s*\b\w+\s+\w+\b(\s+\w+)*\s*(,\s*\b\w+\s+\w+\b(\s+\w+)*\s*)*)$', cast):
            raise forms.ValidationError("Cast non nel formato corretto")
        return cast

    def clean_duration(self):
        duration = self.cleaned_data.get('duration')
        if duration <= 0:
            raise forms.ValidationError("La durata deve essere un numero positivo.")
        if self.instance.pk and duration != self.original_duration:
            self.check_screening_overlaps(duration)
        return duration

    def clean_poster(self):
        poster = self.cleaned_data.get('poster')
        if poster and hasattr(poster, 'content_type'):
            if not poster.content_type.startswith('image'):
                raise forms.ValidationError("Formato immagine non valido. Utilizza un formato di immagine valido.")
        return poster

    def check_screening_overlaps(self, new_duration):
        screenings = Screening.objects.filter(movie=self.instance)
        for screening in screenings:
            end_time = screening.start_time + timedelta(minutes=new_duration)
            overlapping_screenings = Screening.objects.filter(
                room=screening.room,
                start_time__lt=end_time,
                start_time__gte=screening.start_time
            ).exclude(id=screening.id)
            if overlapping_screenings.exists():
                raise forms.ValidationError("La modifica della durata crea una sovrapposizione con una proiezione esistente.")

class MovieSearchForm(forms.Form):
    title = forms.CharField(max_length=255, required=False, label='Titolo')
    cast = forms.CharField(max_length=255, required=False, label='Cast')
    genre = forms.CharField(max_length=255, required=False, label='Genere')
    director = forms.CharField(max_length=255, required=False, label='Regista')
    order_by = forms.ChoiceField(
        required=False,
        choices=[
            ('title', 'Titolo (A-Z)'),
            ('-title', 'Titolo (Z-A)'),
        ],
        label='Ordina per'
    )