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

1. Clone the repository
2. Install requirements:
```
pip install -r requirements.txt
```
3. Run migrations:
```
python manage.py migrate
```
4. Start the development server:
```
python manage.py runserver
```

## API Endpoints

- `GET /api/events/` - List all events
- `POST /api/events/` - Create new event
- `GET /api/events/{id}/` - Get event details
- `PUT /api/events/{id}/` - Update event
- `DELETE /api/events/{id}/` - Delete event
