"""
Django settings for clubs_and_events project.

Generated by 'django-admin startproject' using Django 3.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from datetime import timedelta
from google.oauth2 import service_account
from pathlib import Path

from core.utils.loaders import load_key, load_project_path


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = load_key(key='secret', decrypt=True)


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    '127.0.0.1',
    'https://it-community-dev-03.et.r.appspot.com/',
    '*'
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_cleanup.apps.CleanupConfig',
    'rest_framework',
    'rest_framework.authtoken',
    'asset',
    'category',
    'community',
    'core',
    'generator',
    'membership',
    'misc',
    'notification',
    'user',
    'corsheaders',
]

CORS_ORIGIN_ALLOW_ALL = True

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'crum.CurrentRequestUserMiddleware',
]

ROOT_URLCONF = 'clubs_and_events.urls'

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

WSGI_APPLICATION = 'clubs_and_events.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': load_key(key='db', decrypt=True)[0],
        'USER': load_key(key='db', decrypt=True)[1],
        'PASSWORD': load_key(key='db', decrypt=True)[2],
        'HOST': load_key(key='db', decrypt=True)[3],
        'PORT': '3306'
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Bangkok'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = 'static'


# Authentication Settings

AUTH_USER_MODEL = 'user.User'
AUTHENTICATION_BACKENDS = [
   'user.authentication.AuthenticationBackend',
]


# Django REST Framework Configuration

REST_FRAMEWORK = {
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication'
    ]
}


# LDAP Settings

ENABLE_LDAP = True
LDAP_URL = load_key(key='ldap', decrypt=True)[0]
LDAP_BIND_USERNAME = load_key(key='ldap', decrypt=True)[1]
LDAP_BIND_PASSWORD = load_key(key='ldap', decrypt=True)[2]
LDAP_BASE = 'DC=it,DC=kmitl,DC=ac,DC=th'
LDAP_USER_GROUPS = (
    {'sub_base': 'OU=Student',  'user_group': 'student',  'display_name': 'Student',       'is_staff': False},
    {'sub_base': 'OU=Lecturer', 'user_group': 'lecturer', 'display_name': 'Lecturer',      'is_staff': True},
    {'sub_base': 'OU=Support',  'user_group': 'support',  'display_name': 'Support Staff', 'is_staff': True}
)
LDAP_USERNAME_FIELD = 'sAMAccountName'
LDAP_DISPLAY_NAME_FIELD = 'displayName'


# Email Settings

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = '587'
EMAIL_HOST_USER = 'community.it.kmitl@gmail.com'
EMAIL_HOST_PASSWORD = load_key(key='email', decrypt=True)
EMAIL_USE_TLS = True


# Notification Settings

EMAIL_DOMAIN_NAME = 'it.kmitl.ac.th'
EMAIL_NOTIFICATIONS = False
SEND_IMAGES_AS_ATTACHMENTS = False
FRONT_END_URL = 'https://napontunglukmongkol.github.io/clubs-and-events-frontend/#/'


# Media Path Settings

MEDIA_URL = '/media/'
MEDIA_ROOT = load_project_path()


# Storage Settings

STORAGE_BASE_DIR = '_storage'
DO_IMAGE_DOWNSCALING = True
MAX_ANNOUNCEMENT_IMAGE_DIMENSION = 2048, 2048
MAX_ALBUM_IMAGE_DIMENSION = 4096, 4096
MAX_COMMUNITY_LOGO_DIMENSION = 1024, 1024
MAX_COMMUNITY_BANNER_DIMENSION = 2048, 2048
MAX_PROFILE_PICTURE_DIMENSION = 512, 512


# Club Approval and Renewal Settings

CLUB_VALID_MONTH = 7
CLUB_VALID_DAY = 31
CLUB_ADVANCED_RENEWAL = timedelta(days=60)
STUDENT_COMMITTEE_ADVISOR_NAME = 'ดร.อนันตพัฒน์ อนันตชัย'
STUDENT_COMMITTEE_PRESIDENT_NAME = 'นายธนพนธ์ วงศ์ประเสริฐ'


# Comment Settings

COMMENT_LIMIT_PER_INTERVAL = 2
COMMENT_INTERVAL_TIME = timedelta(minutes=5)


# Vote Settings

VOTE_LIMIT_PER_EVENT = 3


# Natural Language Processing (NLP) Settings

NLP_EN_MODEL = 'en_core_web_sm'


# Google Cloud Storage
# Comment all variables in this section to disable Google Cloud Storage and use local storage

GOOGLE_APPLICATION_CREDENTIALS = '_keys/it-community-dev-03-caaeadc2e996.json'
DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
GS_PROJECT_ID = 'it-community-dev-03'
GS_CREDENTIALS = service_account.Credentials.from_service_account_file('_keys/it-community-dev-03-caaeadc2e996.json')
GS_BUCKET_NAME = 'it-community-dev-03.appspot.com'
GS_DEFAULT_ACL = 'publicRead'
