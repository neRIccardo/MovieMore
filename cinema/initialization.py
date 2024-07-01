import json, os, random, shutil
import sys
from screenings.models import *
from bookings.models import *
from django.contrib.auth.models import User, Group
from django.db import connection
from datetime import datetime, timedelta


def reset_id_counter(table_name):
    with connection.cursor() as cursor:
        cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table_name}';")


def delete_folders():
    folders = ["static/uploaded_posters", "static/uploaded_profile_pictures"]
    for folder in folders:
        try:
            if os.path.exists(folder):
                shutil.rmtree(folder)
                print(f"Cartella eliminata: '{folder}'")
        except FileNotFoundError:
            pass
    

def init_movies():
    if Movie.objects.exists():
        return

    with open(r'{}\static\json\films.json'.format(os.getcwd()), 'r') as file:
        movies_data = json.load(file)

    for movie_data in movies_data:
        movie = Movie(
            title = movie_data['fields']['title'],
            description = movie_data['fields']['description'],
            poster = movie_data['fields']['poster'],
            release_date = movie_data['fields']['release_date'],
            cast = movie_data['fields']['cast'],
            duration = movie_data['fields']['duration'],
            genre = movie_data['fields']['genre'],
            director = movie_data['fields']['director']
        )
        movie.save()


import json
from django.contrib.auth.models import User, Group

def init_users():
    with open('static/json/users.json', 'r') as f:
        users_data = json.load(f)

    # Creazione o recupero dei gruppi
    group_admin, created = Group.objects.get_or_create(name='AmministratoriCinema')
    group_standard, created = Group.objects.get_or_create(name='UtentiRegistrati')

    # Creazione dell'utente superuser
    superuser, created = User.objects.get_or_create(username="AdminR", defaults={'is_superuser': True, 'is_staff': True})
    if created:
        superuser.set_password("progettocinema")
        superuser.save()
    superuser.groups.add(group_admin)

    # Creazione degli utenti admin
    for i in range(1, 4):
        admin_user, created = User.objects.get_or_create(username=f"adm{i}")
        if created:
            admin_user.set_password("progettocinema")
            admin_user.save()
        admin_user.groups.add(group_admin)

    # Creazione degli utenti standard
    for user_data in users_data:
        username = user_data['fields']['user']
        password = user_data['fields']['password']

        user, created = User.objects.get_or_create(username=username)
        if created:
            user.set_password(password)
            user.save()
        user.groups.add(group_standard)


def init_screening_rooms():
    if ScreeningRoom.objects.exists():
        return

    with open(r'{}\static\json\screening_rooms.json'.format(os.getcwd()), 'r') as file:
        rooms_data = json.load(file)

    for room_data in rooms_data:
        screening_rooms = ScreeningRoom(
            name = room_data['fields']['name'],
            capacity = room_data['fields']['capacity'], 
        )
        screening_rooms.save()


def init_screenings():
    with open('static/json/films.json', 'r') as f:
        movies_data = json.load(f)

    with open('static/json/screening_rooms.json', 'r') as f:
        rooms_data = json.load(f)

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    max_date = today + timedelta(days=30)

    screenings_data = []

    def generate_random_time():
        return today.replace(hour=random.randint(17, 23), minute=random.randint(0, 3) * 15, second=0, microsecond=0)

    def is_overlapping(room_id, start_time, movie_duration):
        end_time = start_time + timedelta(minutes=movie_duration)
        for screening in screenings_data:
            if screening['fields']['room'] == room_id:
                existing_start = datetime.strptime(screening['fields']['start_time'], "%Y-%m-%dT%H:%M:%SZ")
                existing_movie = next(movie for movie in movies_data if movie['pk'] == screening['fields']['movie'])
                existing_end = existing_start + timedelta(minutes=existing_movie['fields']['duration'])
                if (start_time < existing_end) and (end_time > existing_start):
                    return True
        return False

    for movie in movies_data:
        movie_pk = movie['pk']
        movie_duration = movie['fields']['duration']
        screenings_per_movie = 0
        
        while screenings_per_movie < 5:
            room = random.choice(rooms_data)
            start_date = generate_random_time()
            start_date += timedelta(days=random.randint(0, (max_date - today).days))
            
            if not is_overlapping(room['pk'], start_date, movie_duration):
                price = round(random.uniform(1, 10), 2)
                screening = {
                    "model": "screenings.screening",
                    "pk": len(screenings_data) + 1,
                    "fields": {
                        "movie": movie_pk,
                        "room": room['pk'],
                        "start_time": start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "price": price
                    }
                }
                screenings_data.append(screening)
                screenings_per_movie += 1

    with open('static/json/screenings.json', 'w') as f:
        json.dump(screenings_data, f, indent=4)

    print("JSON per le proiezioni creato con successo!")

    if Screening.objects.exists():
        return

    with open(r'{}\static\json\screenings.json'.format(os.getcwd()), 'r') as file:
        screenings_data = json.load(file)

    for screening_data in screenings_data:
        movie_id = screening_data['fields']['movie']
        room_id = screening_data['fields']['room']
        start_time = screening_data['fields']['start_time']
        price = screening_data['fields']['price']

        if Movie.objects.filter(pk=movie_id).exists() and ScreeningRoom.objects.filter(pk=room_id).exists():
            screening = Screening(
                movie_id=movie_id,
                room_id=room_id,
                start_time=start_time,
                price=price
            )
        screening.save()


def init_bookings():
    with open('static/json/users.json', 'r') as f:
        users_data = json.load(f)

    with open('static/json/screenings.json', 'r') as f:
        screenings_data = json.load(f)

    bookings_data = []

    def get_available_seats(screening_id):
        # Calcola i posti già prenotati per una determinata proiezione
        booked_seats = set()
        for booking in bookings_data:
            if booking['fields']['screening'] == screening_id:
                seats = booking['fields']['seat_numbers'].split('-')
                booked_seats.update(map(int, seats))
        
        # Ottiene la sala di proiezione e la sua capienza
        screening = next(screening for screening in screenings_data if screening['pk'] == screening_id)
        room_id = screening['fields']['room']
        room = ScreeningRoom.objects.get(pk=room_id)
        
        # Calcola i posti disponibili escludendo quelli già prenotati
        available_seats = set(range(1, room.capacity + 1)) - booked_seats
        return sorted(available_seats)  # Converte in lista ordinata

    def generate_seat_numbers(available_seats, seats_to_book):
        # Genera numeri di posti casuali non duplicati
        return sorted(random.sample(available_seats, seats_to_book))

    for user_data in users_data:
        user_pk = user_data['pk']
        username = user_data['fields']['user']
        
        user = User.objects.get(username=username)
        
        bookings_per_user = 0
        
        while bookings_per_user < 10:
            screening = random.choice(screenings_data)
            screening_id = screening['pk']
            available_seats = get_available_seats(screening_id)
            
            if available_seats:
                # Prenota un numero casuale di posti (da 1 a 10, ma non più del numero di posti disponibili)
                seats_to_book = random.randint(1, min(10, len(available_seats)))
                seat_numbers = generate_seat_numbers(available_seats, seats_to_book)
                seat_numbers_str = '-'.join(map(str, seat_numbers))
                
                booking = {
                    "model": "bookings.booking",
                    "pk": len(bookings_data) + 1,
                    "fields": {
                        "user": user_pk,
                        "screening": screening_id,
                        "seats": seats_to_book,
                        "seat_numbers": seat_numbers_str
                    }
                }
                bookings_data.append(booking)
                bookings_per_user += 1

    with open('static/json/bookings.json', 'w') as f:
        json.dump(bookings_data, f, indent=4)

    print("JSON per le prenotazioni creato con successo!")

    if Booking.objects.exists():
        return

    with open(r'{}\static\json\bookings.json'.format(os.getcwd()), 'r') as file:
        bookings_data = json.load(file)

    for booking_data in bookings_data:
        user_id = booking_data['fields']['user']
        screening_id = booking_data['fields']['screening']
        seats = booking_data['fields']['seats']
        seat_numbers = booking_data['fields']['seat_numbers']

        if User.objects.filter(pk=user_id).exists() and Screening.objects.filter(pk=screening_id).exists():
            booking = Booking(
                user_id=user_id,
                screening_id=screening_id,
                seats=seats,
                seat_numbers=seat_numbers
            )
            booking.save()
        else:
            print(f"User or screening does not exist: user_id={user_id}, screening_id={screening_id}")


def erase_db():
    if 'test' in sys.argv:
        return  # Salta l'inizializzazione se si stanno eseguendo i test
    
    print(f"Cancello il DB - Numero di record: Films: {Movie.objects.count()}, Screening Rooms: {ScreeningRoom.objects.count()}, Screenings: {Screening.objects.count()}, Users: {User.objects.count()}, Bookings: {Booking.objects.count()}")
    
    Movie.objects.all().delete()
    ScreeningRoom.objects.all().delete()
    Screening.objects.all().delete()
    Booking.objects.all().delete()
    User.objects.all().delete()

    delete_folders()
    
    print(f"Dati cancellati - Numero di record dopo cancellazione: Films: {Movie.objects.count()}, Screening Rooms: {ScreeningRoom.objects.count()}, Screenings: {Screening.objects.count()}, Users: {User.objects.count()}, Bookings: {Booking.objects.count()}")


def init_db():
    if 'test' in sys.argv:
        return  # Salta l'inizializzazione se si stanno eseguendo i test
    
    reset_id_counter('movies_movie')
    reset_id_counter('auth_user')
    reset_id_counter('users_userprofile')
    reset_id_counter('screenings_screening')
    reset_id_counter('screenings_screeningroom')
    reset_id_counter('bookings_booking')
    init_movies()
    init_users()
    init_screening_rooms()
    init_screenings()
    init_bookings()
    