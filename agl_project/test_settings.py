from .settings import *

# Use a fast sqlite in-memory DB for tests to avoid MySQL test DB creation issues
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Keep other settings as-is (SECRET_KEY, INSTALLED_APPS, etc.)