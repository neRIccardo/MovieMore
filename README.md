# MovieMore project

This project is a Django application to simulate a cinema website. It includes features for managing movies, theaters, bookings, and users.


## Project Setup

Follow these steps to set up and run the application:

### 1. Install pipenv

Make sure pipenv is installed.
Locally install dependencies, then open virtual-environment shell, with:

```bash
pipenv install
pipenv shell
```
### 2. Install the requirements
Install all project dependencies listed in the requirements.txt file:
```bash
pip install -r requirements.txt
```
### 3. Configure the database
Run the migrations to set up the database:
```bash
python manage.py makemigrations
python manage.py migrate
```
### 4. Start the development server
Start the Django development server:
```bash
python manage.py runserver
```
### 5. Usage
Once the server is running, you can access the cinema site and use the available features.
Go to http://localhost:8000/ and start to explore.