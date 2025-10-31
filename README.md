# Event API

A RESTful API built with Django REST Framework for managing events and registrations. This project demonstrates my understanding of backend development and API design.

## Features

- Event creation and management
- User registration for events
- Permission-based access control
- RESTful API endpoints

## Tech Stack

- Python
- Django
- Django REST Framework
- SQLite (for development)

## Setup

1. Clone the repository:
```
git clone https://github.com/moksh5042/Event_Management_System_-Backend_API-.git
cd Event_Management_System_-Backend_API-
```

2. Create and activate virtual environment:
```
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install requirements:
```
pip install -r requirements.txt
```

4. Database Setup:
   - The project uses SQLite by default
   - Create a new database and apply migrations:
```
python manage.py makemigrations
python manage.py migrate
```
   - Create a superuser (admin):
```
python manage.py createsuperuser
```
   Follow the prompts to set username, email, and password

5. Start the development server:
```
python manage.py runserver
```
   The API will be available at http://127.0.0.1:8000/

6. Access the admin interface:
   - Go to http://127.0.0.1:8000/admin
   - Log in with your superuser credentials

## API Endpoints

- `GET /api/events/` - List all events
- `POST /api/events/` - Create new event
- `GET /api/events/{id}/` - Get event details
- `PUT /api/events/{id}/` - Update event
- `DELETE /api/events/{id}/` - Delete event
