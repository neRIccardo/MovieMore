from django.db import models
from screenings.models import Screening
from django.contrib.auth.models import User

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    screening = models.ForeignKey(Screening, on_delete=models.CASCADE, related_name='bookings')
    seats = models.PositiveIntegerField() 
    seat_numbers = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"prenotazione di {self.user.username} per {self.screening}"