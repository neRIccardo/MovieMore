# Generated by Django 5.0.6 on 2024-06-02 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('poster', models.ImageField(blank=True, null=True, upload_to='posters/')),
                ('release_date', models.DateField()),
                ('cast', models.TextField(help_text='List of main actors')),
                ('duration', models.PositiveIntegerField(help_text='Duration in minutes')),
                ('genre', models.CharField(max_length=50)),
                ('director', models.CharField(help_text='Director of the movie', max_length=255)),
            ],
        ),
    ]