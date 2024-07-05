from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

# Utilizza un segnale di Django per creare automaticamente un profilo utente (UserProfile)
# ogni volta che viene creato un nuovo utente (User). Inoltre, salva il profilo utente esistente
# ogni volta che l'utente viene salvato. Questo assicura che ogni utente abbia un profilo associato
# e che il profilo venga aggiornato quando l'utente viene aggiornato

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.userprofile.save()
