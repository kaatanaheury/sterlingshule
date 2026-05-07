
import os
import sys
from pathlib import Path


project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sterling_shule.settings')

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
