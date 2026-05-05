# MarketFlow Africa

A Django starter web app for African market shopping and delivery operations.

## Stack
- Django
- HTML templates
- CSS
- Vanilla JavaScript
- Function-based views only
- HTML `<form>` tags only

## Apps
- `core_app`
- `buyers_app`
- `sellers_app`
- `drivers_app`
- `qa_app`
- `adminops_app`

## Setup
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo
python manage.py runserver
```

## Notes
- Uses SQLite by default.
- Theme is futuristic neon-tech with day/night toggle.
- Sidebar is collapsible.
- All role workflows use function-based views.
- Forms are built with standard HTML forms and manual POST handling.

## Local media storage (development)
Run `python manage.py create_media_folders` to scaffold temporary upload folders under `media/`.
Use cloud object storage (S3, DO Spaces, Cloudinary, etc.) in production.

## Authentication
- Users can log in with either **username + password** or **email + password**.
- Duplicate emails are blocked during registration at the application-validation level.
- Run `python manage.py check_duplicate_emails` before enforcing a database-level unique email constraint.
