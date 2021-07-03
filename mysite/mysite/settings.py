"""
Django settings for mysite project.

Generated by 'django-admin startproject' using Django 3.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# This setup is recommended here: https://www.ultimatedjango.com/learn-django/lessons/define-environments/side/
# However when I use it and try running the server we get 500 error:  no such table: django_session
#BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Extra places for collectstatic to find static files.
# STATICFILES_DIRS = (
#     os.path.join(BASE_DIR, 'static'),
# )

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_env_variable('EMAIL_HOST_PASSWORD')

# SECURITY WARNING: don't run with debug turned on in production!
DB_PASSWORD = False

MEDIA_SERVER = 'https://res.cloudinary.com/hnyiprajv/'

if ENV_ROLE == 'development':
    DEBUG = True
    TEMPLATE_DEBUG = DEBUG
    DB_HOST = 'localhost'
    DB_PASSWORD = get_env_variable('FAMILY_LOCAL_DB_PASS')
    SOURCE_DB_PASSWORD = get_env_variable('FAMILY_LOCAL_DB_PASS') #@TODO: update these to be different

if ENV_ROLE == 'staging': #@TODO: update these to be different
    DEBUG = False
    TEMPLATE_DEBUG = DEBUG
    DB_HOST = get_env_variable('DB_HOST')
    DB_PASSWORD = get_env_variable('DATABASE_PASSWORD')
    SOURCE_DB_PASSWORD = get_env_variable('SOURCE_DATABASE_PASSWORD')

if ENV_ROLE == 'prod': #@TODO: update these to be different
    DEBUG = False
    TEMPLATE_DEBUG = DEBUG
    DB_HOST = get_env_variable('DB_HOST')
    DB_PASSWORD = get_env_variable('DATABASE_PASSWORD')
    SOURCE_DB_PASSWORD = get_env_variable('SOURCE_DATABASE_PASSWORD')

ALLOWED_HOSTS = ['127.0.0.1', 'family-django-stage.herokuapp.com', 'family-django-prod.herokuapp.com']
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
    # 'django_nose',
]

MIDDLEWARE = [
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

# TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

WSGI_APPLICATION = 'mysite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "migration_test5", # "migration_test5_apr10_safe", #
        "USER": "family",
        "PASSWORD": DB_PASSWORD,
        "HOST": DB_HOST,
        "PORT": "5432",
    },
    "source": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "backup_mar30_2021",  # postgres
        "USER": "family",
        "PASSWORD": SOURCE_DB_PASSWORD,
        "HOST": DB_HOST,
        "PORT": "5432",
    }
}

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
