# Generated by Django 5.0.6 on 2024-06-02 16:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0002_alter_booking_seat_numbers_alter_booking_user'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CustomUser',
        ),
    ]