# screenings/tests.py
from django.test import TestCase
from datetime import date, datetime
from django.utils.timezone import make_aware
from movies.models import Movie
from screenings.models import Screening, ScreeningRoom
from screenings.forms import ScreeningForm

class IsOverlappingTest(TestCase):

    def setUp(self):

        # Film di esempio
        self.movie = Movie.objects.create(
            title='Example Movie',
            duration=120, # durata in minuti
            description="Description example",
            release_date=date(2023, 5, 12),
            cast="Example cast",
            genre="Example genre",
            director="Example director",
            poster='static/posters/default_poster.jpg'
        )
        
        # Sala di esempio
        self.room = ScreeningRoom.objects.create(name='Sala 1', capacity=100)
        
        # Proiezioni di esempio
        self.screening1 = Screening.objects.create(
            movie=self.movie,
            room=self.room,
            start_time=make_aware(datetime(2024, 6, 28, 10, 0)),  # 10:00
            price=10.0
        )
        self.screening2 = Screening.objects.create(
            movie=self.movie,
            room=self.room,
            start_time=make_aware(datetime(2024, 6, 28, 14, 0)),  # 14:00
            price=10.0
        )

    def test_no_overlap(self):
        # Testa che una nuova proiezione che non si sovrappone ritorni False
        form = ScreeningForm()
        result = form.is_overlapping(self.room.id, make_aware(datetime(2024, 6, 28, 18, 0)), self.movie.duration)
        self.assertFalse(result)

    def test_overlap_with_existing(self):
        # Testa che una nuova proiezione che si sovrappone ritorni True
        form = ScreeningForm()
        result = form.is_overlapping(self.room.id, make_aware(datetime(2024, 6, 28, 11, 0)), self.movie.duration)
        self.assertTrue(result)

    def test_exact_overlap(self):
        # Testa che una nuova proiezione che si sovrappone esattamente con una esistente ritorni True
        form = ScreeningForm()
        result = form.is_overlapping(self.room.id, self.screening1.start_time, self.movie.duration)
        self.assertTrue(result)

    def test_contained_within(self):
        # Testa che una nuova proiezione contenuta interamente all'interno di una esistente ritorni True
        form = ScreeningForm()
        result = form.is_overlapping(self.room.id, make_aware(datetime(2024, 6, 28, 10, 30)), 30)  # Durata 30 minuti
        self.assertTrue(result)

    def test_overlap_at_end(self):
        # Testa che una nuova proiezione che inizia prima della fine di una esistente ritorni True
        form = ScreeningForm()
        result = form.is_overlapping(self.room.id, make_aware(datetime(2024, 6, 28, 13, 0)), self.movie.duration)
        self.assertTrue(result)

    def test_overlap_at_start(self):
        # Testa che una nuova proiezione che finisce dopo l'inizio di una esistente ritorni True
        form = ScreeningForm()
        result = form.is_overlapping(self.room.id, make_aware(datetime(2024, 6, 28, 9, 0)), self.movie.duration)
        self.assertTrue(result)
    
    def test_no_overlap_when_editing(self):
        # Testa che la modifica di una proiezione esistente non si sovrappone a se stessa
        form = ScreeningForm()
        result = form.is_overlapping(self.room.id, self.screening1.start_time, self.movie.duration, self.screening1.id)
        self.assertFalse(result)

    def test_overlap_with_other_screening_when_editing(self):
        # Testa che la modifica di una proiezione esistente si sovrappone a un'altra proiezione
        form = ScreeningForm()
        result = form.is_overlapping(self.room.id, make_aware(datetime(2024, 6, 28, 11, 0)), self.movie.duration, self.screening2.id)
        self.assertTrue(result)