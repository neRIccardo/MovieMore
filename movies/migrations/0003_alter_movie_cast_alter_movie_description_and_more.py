# Generated by Django 5.0.6 on 2024-06-10 16:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0002_alter_movie_poster'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='cast',
            field=models.TextField(help_text='Lista degli attori principali (nome1 cognome1, nome2 cognome2, ...)'),
        ),
        migrations.AlterField(
            model_name='movie',
            name='description',
            field=models.TextField(help_text='Descrizione del film'),
        ),
        migrations.AlterField(
            model_name='movie',
            name='director',
            field=models.CharField(help_text='Regista del film (nome cognome)', max_length=255),
        ),
        migrations.AlterField(
            model_name='movie',
            name='duration',
            field=models.PositiveIntegerField(help_text='Durata (minuti)'),
        ),
        migrations.AlterField(
            model_name='movie',
            name='genre',
            field=models.CharField(help_text='Genere del film (es. Azione, Fantascienza, Horror, ...)', max_length=50),
        ),
        migrations.AlterField(
            model_name='movie',
            name='poster',
            field=models.ImageField(blank=True, default='static/posters/default_poster.jpg', null=True, upload_to='static/uploaded_posters/'),
        ),
        migrations.AlterField(
            model_name='movie',
            name='release_date',
            field=models.DateField(help_text='Data di uscita (aaaa/mm/gg)'),
        ),
        migrations.AlterField(
            model_name='movie',
            name='title',
            field=models.CharField(help_text='Titolo del film', max_length=255),
        ),
    ]