import environ
import os
import sys
from pathlib import Path
from django.utils.translation import gettext_lazy as _

env = environ.Env()
environ.Env.read_env()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
SHARED_APPS_DIR = BASE_DIR.parent / 'shared_apps'
SHARED_BLOG_STATIC_DIR = SHARED_APPS_DIR / 'blog' / 'static'
if SHARED_APPS_DIR.exists():
    sys.path.insert(0, str(SHARED_APPS_DIR))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]
CORS_ORIGIN_ALLOW_ALL = True
# CSRF_COOKIE_DOMAIN = None
# CSRF_TRUSTED_ORIGINS = []
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_filters',
    "django_htmx",
    'tinymce',
    'phonenumber_field',
    'corsheaders',
    'rosetta',
    'blog',
    'users',
    'utils',
    "product",
    "core",
    'core_game',
    'core_play',
    'poem'
]


BANK_URL=env("BANK_URL")
BANK_USERNAME=env("BANK_USERNAME")
BANK_PASSWORD=env("BANK_PASSWORD")
BANK_CLIENT_ID=env("BANK_CLIENT_ID")

LOGIN_URL = '/login'
LOGOUT_URL = ''
LOGIN_REDIRECT_URL = 'index'
LOGOUT_REDIRECT_URL = 'login'
AUTH_USER_MODEL = 'users.User'
DATA_UPLOAD_MAX_MEMORY_SIZE = 10000000
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240
DAB_FIELD_RENDERER = 'django_admin_bootstrapped.renderers.BootstrapFieldRenderer'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    "django_htmx.middleware.HtmxMiddleware",
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'utils.middleware.ServerErrorExceptionHandler',
]

ROOT_URLCONF = 'yatuk.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'libraries':{
                'customtags': 'utils.customtags'
            }
        },
    },
]

WSGI_APPLICATION = 'yatuk.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env("DATABASE_NAME"),
        'USER':env("DATABASE_USER"),
        'PASSWORD':env("DATABASE_PASSWORD"),
        'HOST':env("DATABASE_HOST"),
        'PORT':env("DATABASE_PORT"),
        'OPTIONS': {}
    }
}

AUTHENTICATION_BACKENDS = (
     'django.contrib.auth.backends.ModelBackend',
)

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
    } ,
]
# translation doc https://testdriven.io/blog/multiple-languages-in-django/
LANGUAGE_CODE = "hy"
LANGUAGE_COOKIE_NAME = "django_language"
LANGUAGES = [
    ("en", "English"),
    ("hy", "Հայերեն"),
    ("ru", "Русский")
]
TIME_ZONE = 'Asia/Yerevan'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale/'),
)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
if SHARED_BLOG_STATIC_DIR.exists():
    STATICFILES_DIRS.append(str(SHARED_BLOG_STATIC_DIR))

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
BLOG_MEDIA_HOST = ""
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
