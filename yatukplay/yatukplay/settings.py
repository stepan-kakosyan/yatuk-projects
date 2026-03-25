import environ
import os
import sys
from pathlib import Path
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration


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
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
ALLOWED_HOSTS = ["*"]
CORS_ORIGIN_ALLOW_ALL = True

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_filters',
    "django_htmx",
    'django.contrib.sitemaps',
    'corsheaders',
    'rosetta',
    'blog',
    "core_play",
    'users',
]

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
    "yatukplay.custom_middleware.CustomMiddleware"
]
AUTH_USER_MODEL = 'users.User'

ROOT_URLCONF = 'yatukplay.urls'

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
            ]
        },
    },
]

WSGI_APPLICATION = 'yatukplay.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env("DATABASE_NAME"),
        'USER': env("DATABASE_USER"),
        'PASSWORD': env("DATABASE_PASSWORD"),
        'HOST': env("DATABASE_HOST"),
        'PORT': env("DATABASE_PORT"),
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
    },
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
BLOG_MEDIA_HOST = "https://cms.yatuk.am"
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

sentry_sdk.init(
    dsn="https://e491a72bcc1649318b6d8eb9e191b5c8@o4504785028186112.ingest.sentry.io/4504785519902720",
    integrations=[
        DjangoIntegration(),
    ],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)

BATON = {
    'SITE_HEADER': 'Yatuk Music',
    'SITE_TITLE': 'Yatuk Music',
    'INDEX_TITLE': 'Admin Dashboard',
    'CONFIRM_UNSAVED_CHANGES': True,
    'SHOW_MULTIPART_UPLOADING': True,
    'ENABLE_IMAGES_PREVIEW': True,
    'CHANGELIST_FILTERS_IN_MODAL': True,
    'CHANGELIST_FILTERS_ALWAYS_OPEN': False,
    'CHANGELIST_FILTERS_FORM': True,
    'COLLAPSABLE_USER_AREA': False,
    'MENU_ALWAYS_COLLAPSED': False,
    'MENU_TITLE': 'Մենյու',
    'MESSAGES_TOASTS': False,
    'LOGIN_SPLASH': '/static/images/login-splash.jpg',
    'MENU': (
        {'type': 'title', 'label': 'main', 'apps': ('core_play', )},
        {'type': 'model', 'label': 'Composers', 'name': 'author', 'app': 'core_play', 'icon': 'fa fa-users'},
        {'type': 'model', 'label': 'Musics', 'name': 'audio', 'app': 'core_play', 'icon': 'fa fa-music'},
    ),
}
