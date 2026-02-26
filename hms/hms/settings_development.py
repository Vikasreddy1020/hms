"""
Django development settings for Hospital Management System.
Uses SQLite for local development.
"""

from hms.settings import *

# Override database settings for local development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Disable Redis caching for local development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Enable debug mode
DEBUG = True

ALLOWED_HOSTS = ['*']

# Allow CORS for all origins in development
CORS_ALLOW_ALL_ORIGINS = True
