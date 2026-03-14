import environ
import os
import sys
from pathlib import Path
from django.utils.translation import gettext_lazy as _

env = environ.Env()
environ.Env.read_env()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


def get_shared_apps_dir():
    configured_dir = env('SHARED_APPS_DIR', default='')
    candidates = []

    if configured_dir:
        candidates.append(Path(configured_dir).expanduser())

    candidates.extend([
        BASE_DIR.parent / 'shared_apps',
        BASE_DIR / 'shared_apps',
        BASE_DIR.parent.parent / 'shared_apps',
    ])

    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()

    return None


SHARED_APPS_DIR = get_shared_apps_dir()
SHARED_BLOG_STATIC_DIR = None
if SHARED_APPS_DIR:
    SHARED_BLOG_STATIC_DIR = SHARED_APPS_DIR / 'blog' / 'static'
    if str(SHARED_APPS_DIR) not in sys.path:
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
    "core",
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
    'yatuk.middleware.SetTheme'
]
AUTH_USER_MODEL = 'users.User'

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
            ]
        },
    },
]

WSGI_APPLICATION = 'yatuk.wsgi.application'


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

BANK_URL = env("BANK_URL")
BANK_USERNAME=env("BANK_USERNAME")
BANK_PASSWORD=env("BANK_PASSWORD")
BANK_CLIENT_ID=env("BANK_CLIENT_ID")
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
LOGIN_URL = "/login"

LOGOUT_REDIRECT_URL = "/"
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
if SHARED_BLOG_STATIC_DIR and SHARED_BLOG_STATIC_DIR.exists():
    STATICFILES_DIRS.append(str(SHARED_BLOG_STATIC_DIR))

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
BLOG_MEDIA_HOST = "https://cms.yatuk.am"
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

BACKGROUNDS = {
    "1": "linear-gradient(to right, #3A6073, #16222A)",
    "2": "linear-gradient(to right, #314755, #26a0da)",
    "3": "linear-gradient(to right, #00467f, #a5cc82)",
    "4": "linear-gradient(to right, #4ca1af, #c4e0e5)",
    "5": "linear-gradient(to right, #136a8a, #267871)",
    "6": "linear-gradient(to right, #00bf8f, #001510)",
    "7": "linear-gradient(to right, #ff0084, #33001b)"
}

BATON = {
    'SITE_HEADER': 'Yatuk Games',
    'SITE_TITLE': 'Yatuk Games',
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
        { 'type': 'title', 'label': 'main', 'apps': ('core', ) },
        { 'type': 'model', 'label': 'Painters', 'name': 'author', 'app': 'core', 'icon': 'fa fa-users' },
        { 'type': 'model', 'label': 'Games', 'name': 'game', 'app': 'core', 'icon': 'fa fa-puzzle-piece' },
    ),
}

EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = env("EMAIL_PORT")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True
