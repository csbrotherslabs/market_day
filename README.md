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
