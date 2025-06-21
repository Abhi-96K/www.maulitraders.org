import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
AUTH_USER_MODEL = 'main.CustomUser'
SECRET_KEY = 'django-insecure-^bgj2dtv-8n$c#&#qa6l4$)ud=j+fw$4cj^ygxu&nz9=!&fiqq'
DEBUG = False
ALLOWED_HOSTS = ['www-maulitraders-org.onrender.com']
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF = 'Store.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'main/templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
WSGI_APPLICATION = 'Store.wsgi.application'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'main/static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'login'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = '1.maulitraders@gmail.com'
EMAIL_HOST_PASSWORD = 'ccfr tuug zrsc ojzy'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
