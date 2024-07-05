from .forms import *
from cinema.views import *
from .models import *

# Class based view per aggiungere una sala
class AddScreeningRoomView(AddItemView):
    model = ScreeningRoom
    form_class = ScreeningRoomForm
    template_name = 'add_screening_room.html'
    success_message = 'Sala aggiunta con successo'

# Class based view per aggiungere una proiezione
class AddScreeningView(AddItemView):
    model = Screening
    form_class = ScreeningForm
    template_name = 'add_screening.html'
    success_message = 'Proiezione aggiunta con successo'

# Class based view per modificare una sala
class EditScreeningRoomView(EditItemView):
    model = ScreeningRoom
    form_class = ScreeningRoomForm
    template_name = 'edit_screening_room.html'
    success_message = 'Sala modificata con successo'
    pk_url_kwarg = 'screeningroom_id'

# Class based view per modificare una priezione
class EditScreeningView(EditItemView):
    model = Screening
    form_class = ScreeningForm
    template_name = 'edit_screening.html'
    success_message = 'Proiezione modificata con successo'
    pk_url_kwarg = 'screening_id'

# Class based view per eliminare una sala
class DeleteScreeningRoomView(DeleteItemView):
    model = ScreeningRoom
    template_name = 'delete_screening_room.html'
    success_message = 'Sala eliminata con successo'
    pk_url_kwarg = 'screeningroom_id'

# Class based view per eliminare una proiezione
class DeleteScreeningView(DeleteItemView):
    model = Screening
    template_name = 'delete_screening.html'
    success_message = 'Proiezione eliminata con successo'
    pk_url_kwarg = 'screening_id'

# Class based view per mostrare la lista delle sale
class ScreeningRoomListView(CustomRequired, ListView):
    model = ScreeningRoom
    template_name = 'list_screening_rooms.html'
    context_object_name = 'screeningrooms'
    paginate_by = 5
    group_required = ['AmministratoriCinema']

    def get_queryset(self): # Metodo che restituisce la queryset delle sale da visualizzare
        queryset = super().get_queryset()
        name = self.request.GET.get('name')
        capacity = self.request.GET.get('capacity')
        if name:
            queryset = queryset.filter(name__icontains=name)
        if capacity:
            queryset = queryset.filter(capacity__icontains=capacity)
        return queryset

    def get_context_data(self, **kwargs): # Metodo per aggiungere dati aggiuntivi al contesto del template
        context = super().get_context_data(**kwargs)
        context['name'] = self.request.GET.get('name', '')
        context['capacity'] = self.request.GET.get('capacity', '')
        return context

# Class based view per mostrare la lista delle proiezioni
class ScreeningListView(CustomRequired, ListView):
    model = Screening
    template_name = 'list_screenings.html'
    context_object_name = 'screenings'
    paginate_by = 10
    group_required = ['AmministratoriCinema']

    def get_queryset(self): # Metodo che restituisce la queryset delle proiezioni da visualizzare
        queryset = super().get_queryset().select_related('movie', 'room')
        search_form = ScreeningsSearchForm(self.request.GET)
        if search_form.is_valid():
            if search_form.cleaned_data['title']:
                queryset = queryset.filter(movie__title__icontains=search_form.cleaned_data['title'])
            if search_form.cleaned_data['genre']:
                queryset = queryset.filter(movie__genre__icontains=search_form.cleaned_data['genre'])
            if search_form.cleaned_data['start_date'] and search_form.cleaned_data['end_date']:
                if search_form.cleaned_data['start_date'] == search_form.cleaned_data['end_date']:
                    queryset = queryset.filter(start_time__date=search_form.cleaned_data['start_date'])
                else:
                    queryset = queryset.filter(start_time__date__range=(search_form.cleaned_data['start_date'], search_form.cleaned_data['end_date']))
            elif search_form.cleaned_data['start_date']:
                queryset = queryset.filter(start_time__gte=search_form.cleaned_data['start_date'])
            elif search_form.cleaned_data['end_date']:
                queryset = queryset.filter(start_time__lte=search_form.cleaned_data['end_date'])
            if search_form.cleaned_data['order_by']:
                queryset = queryset.order_by(search_form.cleaned_data['order_by'])
        return queryset

    def get_context_data(self, **kwargs): # Metodo per aggiungere dati aggiuntivi al contesto del template
        context = super().get_context_data(**kwargs)
        context['search_form'] = ScreeningsSearchForm(self.request.GET)
        return context