# Hospital Management System (HMS)

A full-featured Hospital Management System built with Django and Bootstrap 5.

## Features

- **User Roles**: Admin, Doctor, Patient
- **Appointments**: Book, manage, and track appointments
- **Prescriptions**: Doctors can write prescriptions with medicines
- **Billing**: Invoices and payment tracking
- **Dashboards**: Role-based dashboards for Admin, Doctor, and Patient

## Tech Stack

- Django 4.2
- Django REST Framework
- JWT Authentication
- Bootstrap 5
- PostgreSQL/SQLite
- Redis (caching)

## Running Locally

```
bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver
```

## Access

- **Home**: http://127.0.0.1:8000/
- **Login**: http://127.0.0.1:8000/login/
- **Admin**: http://127.0.0.1:8000/admin/

## Deploy to Render.com (Free 24/7)

1. **Push to GitHub**:
   
```
bash
   git init
   git add .
   git commit -m "HMS v1"
   # Create repository on GitHub and push
   
```

2. **Deploy on Render**:
   - Go to https://render.com and sign up
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Settings:
     - Build Command: `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
     - Start Command: `gunicorn hms.wsgi:application`
   - Click "Deploy"

3. **Your app will be live at**: `https://your-app-name.onrender.com`

## Quick Deploy Option

Use the included `settings_production.py` which uses SQLite (no database setup needed):

```
bash
# Test production settings locally
python manage.py runserver --settings=hms.settings_production
```

## Default Credentials

After creating superuser:
- Admin Panel: `/admin/`
- API: `/api/`

## License

MIT
