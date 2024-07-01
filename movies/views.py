from cinema.views import *
from django.http import Http404


class AddMovieView(AddItemView):
    model = Movie
    form_class = MovieForm
    template_name = 'add_movie.html'
    success_message = 'Film aggiunto con successo'

class EditMovieView(EditItemView):
    model = Movie
    form_class = MovieForm
    template_name = 'edit_movie.html'
    success_message = 'Film modificato con successo'
    pk_url_kwarg = 'movie_id'

class DeleteMovieView(DeleteItemView):
    model = Movie
    template_name = 'delete_movie.html'
    success_message = 'Film eliminato con successo'
    pk_url_kwarg = 'movie_id'

class MovieListView(CustomRequired, ListView):
    model = Movie
    template_name = 'list_movies.html'
    paginate_by = 10  # Mostra 10 film per pagina
    group_required = ['AmministratoriCinema']

    def get_queryset(self):
        queryset = super().get_queryset()
        title = self.request.GET.get('title')
        cast = self.request.GET.get('cast')
        genre = self.request.GET.get('genre')
        director = self.request.GET.get('director')
        order_by = self.request.GET.get('order_by')

        if title:
            queryset = queryset.filter(title__icontains=title)
        if cast:
            queryset = queryset.filter(cast__icontains=cast)
        if genre:
            queryset = queryset.filter(genre__icontains=genre)
        if director:
            queryset = queryset.filter(director__icontains=director)
        if order_by:
            queryset = queryset.order_by(order_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.request.GET.get('title', '')
        context['cast'] = self.request.GET.get('cast', '')
        context['genre'] = self.request.GET.get('genre', '')
        context['director'] = self.request.GET.get('director', '')
        context['order_by'] = self.request.GET.get('order_by', '')
        return context