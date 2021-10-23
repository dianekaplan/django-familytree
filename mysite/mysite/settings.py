"""
Django settings for mysite project.

Generated by 'django-admin startproject' using Django 3.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os, sys
from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# This setup is recommended here: https://www.ultimatedjango.com/learn-django/lessons/define-environments/side/
# But when I use it and try running the server we get 500 error:  no such table: django_session
#BASE_DIR = os.path.dirname(os.path.abspath(__file__))


if any([arg in sys.argv for arg in ['jenkins', 'test']]):
    os.environ['ENV_ROLE'] = 'test'
    os.environ['ROOT_URL'] = 'test'
    os.environ['EMAIL_HOST_PASSWORD'] = 'test'
    DB_DATABASE = 'test'
    DB_USER = 'test'
    DB_PASSWORD = 'test'
    DB_HOST = 'test'

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': DB_DATABASE,
            'USER': DB_USER,
            'PASSWORD': DB_PASSWORD,
            'HOST': DB_HOST,
            'PORT': '5432',
            'DB_OPTIONS': {'sslmode': 'allow'},
        }
    }



    # os.environ['ENV_ROLE'] = 'test'
    # os.environ['ROOT_URL'] = 'test'
    # os.environ['EMAIL_HOST_PASSWORD'] = 'test'
    # # os.environ['DB_DATABASE'] = 'test'
    # # os.environ['DB_HOST'] = 'test'
    # # os.environ['DB_USERNAME'] = 'test'
    # # os.environ['DATABASE_PASSWORD'] = 'test'


# Handling Key Import Errors
def get_env_variable(var_name):
    """ Get the environment variable or return exception """
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the %s environment variable" % var_name
        raise ImproperlyConfigured(error_msg)


# Get ENV VARIABLES key
ENV_ROLE = get_env_variable('ENV_ROLE')
ROOT_URL = get_env_variable('ROOT_URL')

INTERNAL_IPS = [
    # ...
    '127.0.0.1',
    # ...
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_env_variable('EMAIL_HOST_PASSWORD')

# SECURITY WARNING: don't run with debug turned on in production!
DB_PASSWORD = False

MEDIA_SERVER = 'https://res.cloudinary.com/hhuyx4tno/'

from datetime import datetime
LARAVEL_SITE_CREATION = datetime.strptime('2015-12-01', '%Y-%m-%d').date()
DJANGO_SITE_CREATION = datetime.strptime('2021-07-14', '%Y-%m-%d').date()
NEWEST_GENERATION_FOR_GUEST = 13
ADMIN_EMAIL_SEND_FROM = 'diane@ourbigfamilytree.com'
ADMIN_EMAIL_ADDRESS = 'dianekaplan@gmail.com'


if ENV_ROLE == 'development':
    DEBUG = True
    TEMPLATE_DEBUG = DEBUG
    DB_HOST = 'localhost'
    DB_DATABASE = "sept18_2021_backup"
    DB_USER = 'family'
    DB_PASSWORD = get_env_variable('FAMILY_LOCAL_DB_PASS')
    DB_OPTIONS = {'sslmode': 'allow'}
    SOURCE_DB_PASSWORD = get_env_variable('FAMILY_LOCAL_DB_PASS') #@TODO: update these to be different

if ENV_ROLE == 'staging':
    DEBUG = True
    SECURE_SSL_REDIRECT = True
    TEMPLATE_DEBUG = DEBUG
    DB_HOST = get_env_variable('DB_HOST')
    DB_DATABASE = get_env_variable('DB_DATABASE')
    DB_USER = get_env_variable('DB_USERNAME')
    DB_PASSWORD = get_env_variable('DATABASE_PASSWORD')
    DB_OPTIONS = {'sslmode': 'require'}
    SOURCE_DB_PASSWORD = get_env_variable('SOURCE_DATABASE_PASSWORD')  # @TODO: remove now that migration is done?

if ENV_ROLE == 'prod':
    DEBUG = False
    SECURE_SSL_REDIRECT = True
    TEMPLATE_DEBUG = DEBUG
    DB_HOST = get_env_variable('DB_HOST')
    DB_DATABASE = get_env_variable('DB_DATABASE')
    DB_USER = get_env_variable('DB_USERNAME')
    DB_PASSWORD = get_env_variable('DATABASE_PASSWORD')
    DB_OPTIONS = {'sslmode': 'require'}
    SOURCE_DB_PASSWORD = get_env_variable('SOURCE_DATABASE_PASSWORD')  # @TODO: remove now that migration is done?

ALLOWED_HOSTS = ['127.0.0.1', 'family-django-stage.herokuapp.com', 'family-django-prod.herokuapp.com', '.ourbigfamilytree.com']
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Application definition

INSTALLED_APPS = [
    'familytree.apps.FamilytreeConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    "myauth",
    'django_user_agents',
    'debug_toolbar',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Simplified static file serving.
    # https://warehouse.python.org/project/whitenoise/
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware',
]

ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': str(os.path.join(BASE_DIR, 'templates')),
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'familytree.context_processors.include_login_form',
            ],
        },
    },
]

WSGI_APPLICATION = 'mysite.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": DB_DATABASE,
        "USER": DB_USER, #'family',
        "PASSWORD": DB_PASSWORD,
        "HOST": DB_HOST,
        "PORT": "5432",
        "OPTIONS": DB_OPTIONS,
    },
    "source": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "laravel_backup_aug15",
        "USER": DB_USER,
        "PASSWORD": "test", # @TODO: remove now that migration is done?
        "HOST": DB_HOST,
        "PORT": "5432",
    }
}

# TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

# For unit tests we'll use sqlite
import sys
if 'test' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3')
    }


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Email settings
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'postmaster@mg.ourbigfamilytree.com'
EMAIL_HOST_PASSWORD=get_env_variable('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'landing'
