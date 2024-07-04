# MovieMore project

This project is a Django application to simulate a cinema website. It includes features for managing movies, screenings, screening rooms, bookings and users.


## Project Setup

Follow these steps to set up and run the application:

### 1. Clone the repository
```bash
git clone https://github.com/neRIccardo/MovieMore.git
cd MovieMore
```
### 2. Install pipenv

Make sure pipenv is installed.
Locally install dependencies, then open virtual-environment shell with:

```bash
pipenv install
pipenv shell
```
### 3. Install the requirements
Install all project dependencies listed in the requirements.txt file:
```bash
pip install -r requirements.txt
```
### 4. Configure the database
Run the migrations to set up the database:
```bash
python manage.py migrate
```
### 5. Run the following setup file
Run setup.py to populate the DB:
```bash
python setup.py
```
### 6. Start the development server
Start the Django development server:
```bash
python manage.py runserver
```
### 7. Usage
Once the server is running, you can access the cinema site and use the available features.
Go to http://localhost:8000/ and start to explore.

| Role                 | Username                                                                            | Password       |
|----------------------|-------------------------------------------------------------------------------------|----------------|
| Admin (superuser)    | AdminR                                                                              | progettocinema |
| Cinema administrator | adm1 - adm2 - adm3                                                                  | progettocinema |
| Registered User      | marco.rossi93 - giulia.bianchi21 - luca_espo89 - fran.romano88 - 	matteo.conti77   | progettocinema |
| Guest                | /                                                                                   | /              |

Each time setup.py is run, a different situation is created. The Db will be completely deleted and repopulated. The users remain the same but the projections and purchases/bookings will change (only non-administrator users have bookings)
