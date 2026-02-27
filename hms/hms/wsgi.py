"""
WSGI config for HMS project.
"""
import os
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hms.hms.settings')

application = get_wsgi_application()
application = WhiteNoise(application, root='staticfiles')
