from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-flyweight-smartmenu-secret')
DEBUG = 'RENDER' not in os.environ
ALLOWED_HOSTS = ['*'] # In production you might want to specify your actual Render URL here

INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'menuapp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'smartmenu.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'smartmenu.wsgi.application'

DATABASES = {} # No database needed for this demo

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
# Add STATIC_ROOT for Render to collect static files
STATIC_ROOT = BASE_DIR / 'staticfiles'

