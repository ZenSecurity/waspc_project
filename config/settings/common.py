"""
Django settings for waspc project.

Generated by 'django-admin startproject' using Django 1.8.3.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'please_replace_this_secret_key_in_your_new_deployment_instance'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# TODO: need to read about this params more.
ALLOWED_HOSTS = ['*']
CSRF_COOKIE_HTTPONLY = True
# CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_SECONDS = 0
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'


# Application definition

INSTALLED_APPS = (
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.postgres',
    'django.contrib.sessions',
    'django.contrib.staticfiles',

    # Third party
    'rest_framework',
    'djcelery',

    # WASPC components
    'waspc.scanner',
    'waspc.monitoring',
    'waspc.reporting'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'waspc.contrib.logger.middleware.RequestLoggerMiddleware'
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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


ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'waspc',
        'USER': 'waspc',
        'PASSWORD': 'waspc',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Minsk'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'static')


# Celery (Distributed Task Queue)
# http://celery.readthedocs.org/en/latest/configuration.html

BROKER_URL = 'amqp://localhost'
CELERY_RESULT_BACKEND = 'redis://'
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'

CELERY_CREATE_MISSING_QUEUES = True
CELERY_TRACK_STARTED = True
CELERYD_MAX_TASKS_PER_CHILD = 1
CELERY_TASK_RESULT_EXPIRES = 360
CELERYD_TASK_TIME_LIMIT = 360

CELERY_TASK_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/Minsk'

if 'djcelery' in INSTALLED_APPS:
    from djcelery import setup_loader
    setup_loader()


# Django REST framework
# http://www.django-rest-framework.org/api-guide/settings/

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
}


# LOGGING CONFIGURATION
# See: https://docs.djangoproject.com/en/1.8/ref/settings/#logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'waspc_requests.log',
        },
    },
    'loggers': {
        'waspc': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}


# Web Application Security Policy Checker
# https://github.com/ZenSecurity/waspc

WASPC = {
    'scanner': {
        'profile_name': 'wg',
        'target_url': 'http://zensecurity.su'
    },
    'monitoring': {
        'every': 15,
        'period': 'minutes'
    },
    'reporting': {
        'jira': {
            'server': 'https://zensec.atlassian.net',
            'username': 'admin',
            'password': 'adminadmin'
        }
    }
}
