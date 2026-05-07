"""WSGI config for SterlingShule."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sterling_shule.settings")

application = get_wsgi_application()
