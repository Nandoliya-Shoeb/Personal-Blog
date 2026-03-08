"""
WSGI config for personal_blog2 project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'personal_blog2.settings')

application = get_wsgi_application()
