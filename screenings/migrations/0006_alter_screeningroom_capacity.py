# Generated by Django 5.0.6 on 2024-06-23 20:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('screenings', '0005_alter_screening_movie_alter_screening_price_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='screeningroom',
            name='capacity',
            field=models.PositiveIntegerField(),
        ),
    ]
