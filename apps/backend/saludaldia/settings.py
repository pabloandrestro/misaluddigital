import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# carga variables desde el archivo .env ubicado junto a manage.py
load_dotenv(BASE_DIR / ".env")


# --------------------------------------------------
# django
# --------------------------------------------------

SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-cambiar-en-produccion")

DEBUG = os.getenv("DEBUG", "True") == "True"

ALLOWED_HOSTS = os.getenv(
    "ALLOWED_HOSTS",
    "localhost,127.0.0.1"
).split(",")


# --------------------------------------------------
# apps
# --------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",

    "apps.users",
    "apps.documents",
    "apps.sharing",
    "apps.ai_analysis",
    "apps.health_centers",
    "apps.pets",
    "apps.audit",
]


# --------------------------------------------------
# middleware
# --------------------------------------------------

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",

    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# --------------------------------------------------
# urls / wsgi
# --------------------------------------------------

ROOT_URLCONF = "saludaldia.urls"
WSGI_APPLICATION = "saludaldia.wsgi.application"


# --------------------------------------------------
# templates
# --------------------------------------------------

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]


# --------------------------------------------------
# base de datos postgresql / supabase
# --------------------------------------------------

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "postgres"),
        "USER": os.getenv("DB_USER", ""),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", ""),
        "PORT": os.getenv("DB_PORT", "5432"),
        "OPTIONS": {
            "sslmode": os.getenv("DB_SSLMODE", "require"),
        },
    }
}


# --------------------------------------------------
# usuario personalizado
# --------------------------------------------------

AUTH_USER_MODEL = "users.User"


# --------------------------------------------------
# django rest framework
# --------------------------------------------------

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}


# --------------------------------------------------
# jwt
# --------------------------------------------------

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=int(os.getenv("JWT_ACCESS_TOKEN_LIFETIME_MINUTES", "60"))
    ),
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=int(os.getenv("JWT_REFRESH_TOKEN_LIFETIME_DAYS", "7"))
    ),
    "ROTATE_REFRESH_TOKENS": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}


# --------------------------------------------------
# cors
# --------------------------------------------------

CORS_ALLOWED_ORIGINS = [
    os.getenv("FRONTEND_URL", "http://localhost:3000"),
]

CORS_ALLOW_CREDENTIALS = True


# --------------------------------------------------
# supabase
# --------------------------------------------------

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

# buckets
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "medical-documents")

SUPABASE_PROFILE_IMAGE_BUCKET = os.getenv("SUPABASE_PROFILE_IMAGE_BUCKET", "profile-images")


# --------------------------------------------------
# anthropic
# --------------------------------------------------

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")


# --------------------------------------------------
# email
# --------------------------------------------------

EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = True


# --------------------------------------------------
# idioma / zona horaria
# --------------------------------------------------

LANGUAGE_CODE = "es-cl"
TIME_ZONE = "America/Santiago"

USE_I18N = True
USE_TZ = True


# --------------------------------------------------
# static / media
# --------------------------------------------------

STATIC_URL = "/static/"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# --------------------------------------------------
# default pk
# --------------------------------------------------

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"