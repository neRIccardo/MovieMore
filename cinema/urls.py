from django.contrib import admin
from django.urls import path, re_path
from .initialization import *
from .views import *
from users.views import *
from movies.views import *
from screenings.views import *
from bookings.views import *

urlpatterns = [

     #-----MAIN PAGES-----#
    path('admin/', admin.site.urls),
    re_path(r"^$|^\/$|^home\/$", cinema_home, name="home"),
    path('scheduling/', CinemaSchedulingView.as_view(), name="scheduling"),
    path('collection/', CinemaCollectionView.as_view(), name="collection"),

    #-----OPERAZIONI UTENTE-----#
    path('signup/', signup_view, name="signup"),
    path('login/', login_view, name="login"),
    path('logout/', logout_view, name='logout'),
    path('purchase/<int:screening_id>/', PurchaseTicketsView.as_view(), name='purchase_tickets'),

     #-----PROFILO UTENTE-----#
    path('profile/', ViewProfileView.as_view(), name="profile"), 
    path('profile/edit/', EditProfileView.as_view(), name='edit_profile'),
    path('profile/bookings/', BookingListView.as_view(), name='user_bookings'),

     #-----OPERAZIONI AMMINISTRATORI-----#
    path('management/', ManagementPanelView.as_view(), name="management"),
    path('management/add_movie/', AddMovieView.as_view(), name='add_movie'),
    path('management/edit_movie/', MovieListView.as_view(), name='list_movies'),
    path('management/edit_movie/<int:movie_id>/', EditMovieView.as_view(), name='edit_movie'),
    path('management/delete_movie/<int:movie_id>/', DeleteMovieView.as_view(), name='delete_movie'),
    path('management/add_screeningroom/', AddScreeningRoomView.as_view(), name='add_screeningroom'),
    path('management/edit_screeningroom/', ScreeningRoomListView.as_view(), name='list_screeningrooms'),
    path('management/edit_screeningroom/<int:screeningroom_id>/', EditScreeningRoomView.as_view(), name='edit_screeningroom'),
    path('management/delete_screeningroom/<int:screeningroom_id>/', DeleteScreeningRoomView.as_view(), name='delete_screeningroom'),
    path('management/add_screening/', AddScreeningView.as_view(), name='add_screening'),
    path('management/edit_screening/', ScreeningListView.as_view(), name='list_screenings'),
    path('management/edit_screening/<int:screening_id>/', EditScreeningView.as_view(), name='edit_screening'),
    path('management/delete_screening/<int:screening_id>/', DeleteScreeningView.as_view(), name='delete_screening'),

    #-----CATTURA ERRORI-----#
    re_path(r'^.*$', custom_404_view)
]
