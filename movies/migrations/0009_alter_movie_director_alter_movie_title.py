# Generated by Django 5.0.6 on 2024-06-30 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0008_alter_movie_release_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='director',
            field=models.CharField(help_text='Regista del film ("nome cognome" e NO mumeri)', max_length=50),
        ),
        migrations.AlterField(
            model_name='movie',
            name='title',
            field=models.CharField(help_text='Titolo del film', max_length=50),
        ),
    ]
