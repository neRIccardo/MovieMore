from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from movies.models import Movie
from screenings.models import ScreeningRoom, Screening
from .models import Booking
from .views import *
from django.contrib.messages import get_messages

class PurchaseTicketsViewTest(TestCase):

    def setUp(self):
        # creazione degli oggetti necessari per il test
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.movie = Movie.objects.create(
            title='Test Movie',
            description='Test Description',
            release_date=timezone.now().date(),
            cast='Actor 1, Actor 2',
            duration=120,
            genre='Test Genre',
            director='Test Director'
        )
        self.screening_room = ScreeningRoom.objects.create(name='Sala 1', capacity=100)
        self.screening = Screening.objects.create(
            movie=self.movie,
            room=self.screening_room,
            start_time=timezone.now() + timezone.timedelta(days=1),
            price=10.0
        )
        self.booking_url = reverse('purchase_tickets', kwargs={'screening_id': self.screening.id})


    def test_view_uses_correct_template(self):
        # Testa che la risorsa esista e che venga mostrato il template corretto
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.booking_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'purchase_ticket.html')

    def test_data(self):
        # Testa la correttezza del context e dei dati nel form
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.booking_url)
        form = response.context['form']
        self.assertEqual(response.context['screening'], self.screening)
        self.assertEqual(response.context['available_seats'], self.screening_room.capacity)
        self.assertEqual(form.initial['first_name'], self.user.first_name)
        self.assertEqual(form.initial['last_name'], self.user.last_name)
        self.assertEqual(form.initial['email'], self.user.email)

    def test_booking_success(self):
        # Testa che un nuovo acquisto avvenga correttamente
        self.client.login(username='testuser', password='testpass')
        post_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'cc_name': 'Test User',
            'cc_number': '1234567812345678',
            'cc_expiration': '12/25',
            'cc_cvv': '123',
            'seats': 2
        }
        response = self.client.post(self.booking_url, post_data)
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(Booking.objects.count(), 1)
        booking = Booking.objects.first()
        self.assertEqual(booking.user, self.user)
        self.assertEqual(booking.screening, self.screening)
        self.assertEqual(booking.seats, 2)

    def test_dispatch_redirects_if_screening_not_found(self):
        # Testa il reindirizzamento ad una pagina di errore se non esiste la proiezione
        response = self.client.get(reverse('purchase_tickets', kwargs={'screening_id': 9999}))
        self.assertEqual(response.status_code, 404)

    def test_booking_invalid_form(self):
        # Testa che vengano segnalati errori se il form di acquisto non è corretto
        self.client.login(username='testuser', password='testpass')
        post_data = {
            'first_name': 'Test1', # no numeri
            'last_name': 'Us3r', # no numeri
            'email': 'invalid_email',
            'cc_name': 'Test User 1', # no numeri
            'cc_number': '1234567812345678123456', # troppi numeri
            'cc_expiration': '12/22', # scaduta
            'cc_cvv': '13', # non sono 3 numeri
            'seats': 0 # almeno 1
        }
        response = self.client.post(self.booking_url, post_data)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)
        self.assertIn('last_name', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('cc_name', form.errors)
        self.assertIn('cc_number', form.errors)
        self.assertIn('cc_expiration', form.errors)
        self.assertIn('cc_cvv', form.errors)
        self.assertIn('seats', form.errors)

    def test_generate_seat_numbers(self):
        # Testa che la generazione dei posti sia corretta (NO posti duplicati e #posti generati = #posti acquistati)
        booked_seats = Booking.objects.create(
            user=self.user,
            screening=self.screening,
            seats=2,
            seat_numbers='1,3'
        )
        self.screening_room.capacity = 4
        available_seats = generate_seat_numbers(self.screening, 1)
        available_seats_str = ','.join(map(str, available_seats))
        # siccome la capacità è 4 ed i posti "1-2" sono già occupati, verrà generato un posto random scelto tra "2" e "4"
        self.assertTrue(available_seats_str == '2' or available_seats_str == '4')


    def test_dispatch_redirects_if_sold_out(self):
        # Testa che non sia possibile acquistare una proiezione soldout e che si venga reindirizzati correttamente
        Booking.objects.create(user=self.user, screening=self.screening, seats=self.screening_room.capacity)
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.booking_url)
        self.assertRedirects(response, reverse('home'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Proiezione sold out.')