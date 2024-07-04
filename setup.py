import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cinema.settings')
django.setup()

from cinema.initialization import erase_db, init_db

erase_db()
init_db()
