from django.db import models

class Movie(models.Model):
    title = models.CharField(max_length = 50, help_text="Titolo del film")
    description = models.TextField(help_text="Descrizione del film")
    poster = models.ImageField(upload_to = 'static/uploaded_posters/', null = True, blank = True, default='static/posters/default_poster.jpg')
    release_date = models.DateField(help_text="Data di uscita (aaaa-mm-gg)")
    cast = models.TextField(help_text = "Lista degli attori principali (\"nome1 cognome1, nome2 cognome2, ...\" e NO numeri)")
    duration = models.PositiveIntegerField(help_text = "Durata (minuti)")
    genre = models.CharField(max_length = 50, help_text="Genere del film (es. \"Azione, Fantascienza, Horror, ...\" e NO numeri)")
    director = models.CharField(max_length = 50, help_text = "Regista del film (\"nome cognome\" e NO mumeri)")

    def __str__(self):
        return self.title