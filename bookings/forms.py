import datetime
from django import forms
from bookings.models import Booking


def validate_cvv(value):
    if not value.isdigit() or len(value) != 3:
        raise forms.ValidationError("Il CVV deve essere composto da 3 cifre.")

def validate_expiration_date(value):
    try:
        expiration_date = datetime.datetime.strptime(value, "%m/%y")
        if expiration_date < datetime.datetime.now():
            raise forms.ValidationError("La carta è scaduta.")
    except ValueError:
        raise forms.ValidationError("Formato della data di scadenza non valido. Usa MM/YY.")

def validate_name(value):
    if any(char.isdigit() for char in value):
        raise forms.ValidationError("II numeri non sono permessi.")

def validate_card_number(value):
    if not value.isdigit() or not (13 <= len(value) <= 16):
        raise forms.ValidationError("Il numero della carta deve essere composto da 13 a 16 cifre.")

class BookingForm(forms.ModelForm):
    first_name = forms.CharField(label="Nome", max_length=50, required=True, validators=[validate_name])
    last_name = forms.CharField(label="Cognome", max_length=50, required=True, validators=[validate_name])
    email = forms.EmailField(label="Email", required=True)
    cc_name = forms.CharField(label="Intestatario della carta", max_length=100, required=True, validators=[validate_name])
    cc_number = forms.CharField(label="Numero della carta", max_length=16, min_length=13, required=True, validators=[validate_card_number])
    cc_expiration = forms.CharField(label="Scadenza", max_length=5, required=True, validators=[validate_expiration_date])
    cc_cvv = forms.CharField(label="CVV", max_length=3, required=True, validators=[validate_cvv])
    seats = forms.IntegerField(min_value=1, label="Numero di posti", required=True)

    class Meta:
        model = Booking
        fields = ['first_name', 'last_name', 'email', 'cc_name', 'cc_number', 'cc_expiration', 'cc_cvv', 'seats']