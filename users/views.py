from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import Group
from django.views import View
from .forms import UserProfileForm
from .models import UserProfile
from django.urls import reverse_lazy
from bookings.models import Booking
from django.views.generic import ListView
from cinema.views import CustomRequired

# Function view per la renderizzazione della registrazione
def signup_view(request):
    if request.user.is_authenticated:
        messages.success(request, 'Effettua il logout per poter registrare un nuovo profilo.')
        return redirect('home')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            utenti_registrati_group = Group.objects.get(name='UtentiRegistrati')
            user.groups.add(utenti_registrati_group)
            login(request, user)
            messages.success(request, 'Registrazione avvenuta con successo. Benvenuto su MovieMore, login effettuato automaticamente.')
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

# Function view per la renderizzazione del login
def login_view(request):
    if request.user.is_authenticated:
        messages.success(request, 'Hai già eseguito l\'accesso.')
        return redirect('home')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Accesso effettuato con successo. Bentornato su MovieMore.')
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

# Function view per eseguire il logout
def logout_view(request):
    if not request.user.is_authenticated:
        messages.success(request, 'Devi prima accedere per poter eseguire il logout.')
    else:
        logout(request)
        messages.success(request, 'Logout eseguito con successo.')
    return redirect(reverse_lazy('home'))

# Class based view per modificare il proprio profilo
class EditProfileView(CustomRequired, View):
    group_required = None

    def get(self, request): # Metodo che tenta di ottenere il profilo dell'utente corrente
        try:
            profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)
        
        form = UserProfileForm(instance=profile)
        return render(request, 'edit_profile.html', {'form': form})

    def post(self, request): # Metodo che tenta di ottenere il profilo dell'utente corrente e gestire il POST delle modifiche ad esso
        try:
            profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)
        
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profilo aggiornato con successo.')
            return redirect('profile')
        
        return render(request, 'edit_profile.html', {'form': form})

# Class based view per visualizzare il proprio profilo
class ViewProfileView(CustomRequired, View):
    group_required = None

    def get(self, request): # Metodo che tenta di ottenere il profilo dell'utente corrente
        try:
            profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)
        
        return render(request, 'profile.html', {'profile': profile})

# Class based view per visualizzare gli acquisti di un certo utente
class BookingListView(CustomRequired, ListView):
    model = Booking
    template_name = 'user_bookings.html'
    context_object_name = 'bookings'
    paginate_by = 5
    group_required = None

    def get_queryset(self): # Metodo che restituisce la queryset degli acquisti da visualizzare
        return Booking.objects.filter(user=self.request.user).order_by('screening__start_time')

    def get_context_data(self, **kwargs): # Metodo per aggiungere dati aggiuntivi al contesto del template
        context = super().get_context_data(**kwargs)
        return context