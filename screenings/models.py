from django.db import models
from movies.models import Movie

# Classe che rappresenta un oggetto di tipo ScreeningRoom
class ScreeningRoom(models.Model):
    name = models.CharField(max_length = 50, help_text="Nome della sala (es. \"Sala 1\", \"Sala 2\", ...)")
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return self.name

# Classe che rappresenta un oggetto di tipo Screening
class Screening(models.Model):
    movie = models.ForeignKey(Movie, on_delete = models.CASCADE, related_name='screenings')
    room = models.ForeignKey(ScreeningRoom, on_delete = models.CASCADE, related_name='screenings')
    start_time = models.DateTimeField()
    price = models.FloatField(default=None, help_text="Prezzo in €")

    def __str__(self):
        return f"{self.movie.title} in {self.room.name} alle {self.start_time}"
