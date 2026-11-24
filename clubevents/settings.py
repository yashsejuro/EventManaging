"""Production-ready Django settings for ClubEvents.

Configuration values are loaded from environment variables (and an optional
local .env file in development), with safe local defaults when running tests
or local development servers.
"""

import logging
import os
import sys
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional fallback if not installed
    load_dotenv = None


BASE_DIR = Path(__file__).resolve().parent.parent
if load_dotenv is not None:
    load_dotenv(BASE_DIR / ".env")


def _env(*names, default=""):
    """Return the first populated environment variable from names."""
    for name in names:
        value = os.environ.get(name)
        if value is not None and value != "":
            return value
    return default


def _env_bool(*names, default=False):
    """Parse common truthy/falsy strings from environment variables."""
    fallback = "True" if default else "False"
    raw = _env(*names, default=fallback)
    return str(raw).strip().lower() in {"1", "true", "yes", "on"}


def _env_list(*names, default=""):
    """Split comma-separated environment settings cleanly."""
    raw = _env(*names, default=default)
    return [item.strip() for item in raw.split(",") if item.strip()]


DEV_SECRET_KEY = "dev-only-change-this-clubevents-key"
SECRET_KEY = _env("SECRET_KEY", "DJANGO_SECRET_KEY", default=DEV_SECRET_KEY)
DEBUG = _env_bool(
    "DEBUG",
    "DJANGO_DEBUG",
    default=not bool(os.environ.get("VERCEL")),
)

IS_COLLECTSTATIC = len(sys.argv) > 1 and sys.argv[1] == "collectstatic"
if not DEBUG and not IS_COLLECTSTATIC and SECRET_KEY == DEV_SECRET_KEY:
    raise ImproperlyConfigured(
        "SECRET_KEY (or DJANGO_SECRET_KEY) must be set when DEBUG is False."
    )

ALLOWED_HOSTS = _env_list(
    "ALLOWED_HOSTS",
    "DJANGO_ALLOWED_HOSTS",
    default="localhost,127.0.0.1,.vercel.app",
)
CSRF_TRUSTED_ORIGINS = _env_list(
    "CSRF_TRUSTED_ORIGINS",
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    default="",
)

for vercel_host in (
    os.environ.get("VERCEL_URL"),
    os.environ.get("VERCEL_BRANCH_URL"),
    os.environ.get("VERCEL_PROJECT_PRODUCTION_URL"),
):
    if vercel_host:
        host = vercel_host.strip().lower()
        if "://" in host:
            host = host.split("://", 1)[1].split("/", 1)[0]
        if host:
            if host not in ALLOWED_HOSTS:
                ALLOWED_HOSTS.append(host)
            origin = f"https://{host}"
            if origin not in CSRF_TRUSTED_ORIGINS:
                CSRF_TRUSTED_ORIGINS.append(origin)

if os.environ.get("VERCEL"):
    if ".vercel.app" not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(".vercel.app")
    if "https://*.vercel.app" not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append("https://*.vercel.app")

# HTTPS / proxy security headers
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = _env_bool(
    "SECURE_SSL_REDIRECT",
    "DJANGO_SECURE_SSL_REDIRECT",
    default=not DEBUG,
)
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SAMESITE = "Lax"
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SECURE_HSTS_SECONDS = int(
    _env("SECURE_HSTS_SECONDS", default="31536000" if not DEBUG else "0")
)
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
    "events",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "clubevents.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "clubevents.wsgi.application"
ASGI_APPLICATION = "clubevents.asgi.application"

database_url = _env("DATABASE_URL")
if os.environ.get("VERCEL") and not database_url:
    logging.getLogger(__name__).warning(
        "DATABASE_URL is not set on Vercel; falling back to ephemeral /tmp SQLite."
    )
    database_url = "sqlite:////tmp/clubevents.sqlite3"

DATABASES = {
    "default": dj_database_url.config(
        default=database_url or f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        conn_health_checks=True,
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles_build" / "static"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Cloudinary for uploaded media only; WhiteNoise serves static files cleanly.
CLOUDINARY_URL = _env("CLOUDINARY_URL")
CLOUDINARY_CLOUD_NAME = _env("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = _env("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = _env("CLOUDINARY_API_SECRET")
HAS_CLOUDINARY = bool(
    CLOUDINARY_URL
    or (CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET)
)

if CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET:
    CLOUDINARY_STORAGE = {
        "CLOUD_NAME": CLOUDINARY_CLOUD_NAME,
        "API_KEY": CLOUDINARY_API_KEY,
        "API_SECRET": CLOUDINARY_API_SECRET,
        "SECURE": True,
    }

DEFAULT_MEDIA_STORAGE = (
    "clubevents.storage.ClubEventsMediaStorage"
    if HAS_CLOUDINARY
    else "django.core.files.storage.FileSystemStorage"
)

STORAGES = {
    "default": {
        "BACKEND": DEFAULT_MEDIA_STORAGE,
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Transactional email (Brevo, Resend, or Gmail SMTP via env vars)
EMAIL_HOST = _env("EMAIL_HOST")
EMAIL_PORT = int(_env("EMAIL_PORT", default="587"))
EMAIL_HOST_USER = _env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = _env("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = _env_bool("EMAIL_USE_TLS", default=True)
EMAIL_USE_SSL = _env_bool("EMAIL_USE_SSL", default=False)
EMAIL_TIMEOUT = 10
DEFAULT_FROM_EMAIL = _env(
    "DEFAULT_FROM_EMAIL",
    default="ClubEvents <noreply@clubevents.local>",
)
SERVER_EMAIL = DEFAULT_FROM_EMAIL

if EMAIL_HOST:
    EMAIL_BACKEND = _env(
        "EMAIL_BACKEND",
        default="django.core.mail.backends.smtp.EmailBackend",
    )
else:
    EMAIL_BACKEND = _env(
        "EMAIL_BACKEND",
        default="django.core.mail.backends.console.EmailBackend",
    )

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "events:home"
LOGOUT_REDIRECT_URL = "events:home"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name}: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": _env("LOG_LEVEL", default="INFO"),
    },
    "loggers": {
        "django.request": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "events": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "accounts": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
