from __future__ import annotations

from pathlib import Path

import environs

BASE_DIR = Path(__file__).resolve().parent.parent
APPS_DIR = BASE_DIR / "upkeep"

env = environs.Env()
env.read_env(str(BASE_DIR / ".env"), recurse=False)

DEBUG = env.bool("DEBUG", default=False)
SECRET_KEY = env.str("DJANGO_SECRET_KEY", default="NOT A SECRET")
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

# e.g. DJANGO_DATABASE_URL=postgres:///${REPO_NAME}?pool=true
# uses a peer connection over default Unix socket with OPTION pool (default)
DATABASES = {
    "default": (
        env.dj_db_url(
            "DJANGO_DATABASE_URL",
            default=f"sqlite:///{BASE_DIR}/db.sqlite3",
        )
    ),
}

# e.g. DJANGO_DATABASE_OPTIONS='{"pool": {"min_size": 2, "max_size": 4}}'
if env.str("DJANGO_DATABASE_OPTIONS", ""):
    DATABASES["default"]["OPTIONS"] = DATABASES["default"].get("OPTIONS", {}) | env.json("DJANGO_DATABASE_OPTIONS")  # fmt: off


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "crispy_forms",
    "crispy_bootstrap5",
    "django_htmx",
    "config",
    "upkeep.ui",
    "upkeep.core",
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
    "django_htmx.middleware.HtmxMiddleware",
]

if DEBUG:
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
    DEBUG_TOOLBAR_CONFIG = {"ROOT_TAG_EXTRA_ATTRS": "hx-preserve"}
    INTERNAL_IPS = ["127.0.0.1"]


ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [APPS_DIR / "ui" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"

CRISPY_TEMPLATE_PACK = "bootstrap5"

USE_TZ = True

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

STATIC_URL = "static/"

# STATIC_ROOT is where collectstatic will collect files for deployment
STATIC_ROOT = env.str("DJANGO_STATIC_ROOT", default=str(BASE_DIR / "static"))

# STATICFILES_DIR is where "django.contrib.staticfiles" looks during development
STATICFILES_DIRS = [APPS_DIR / "ui" / "static"]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "rich": {"datefmt": "[%X]"},
        "console": {
            "format": "[{levelname}] {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "rich.logging.RichHandler",
            "level": "DEBUG",
            "formatter": "rich",
            "rich_tracebacks": True,
            "tracebacks_show_locals": True,
        }
        if DEBUG
        else {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "console",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
        "conf": {
            "handlers": ["console"],
            "level": env.log_level("LOG_LEVEL", default="INFO"),
            "propagate": True,
        },
        "upkeep": {
            "handlers": ["console"],
            "level": env.log_level("LOG_LEVEL", default="INFO"),
            "propagate": True,
        },
    },
}
