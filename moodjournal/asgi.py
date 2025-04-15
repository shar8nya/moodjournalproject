"""
ASGI config for moodjournal project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moodjournal.settings')

application = get_asgi_application()
