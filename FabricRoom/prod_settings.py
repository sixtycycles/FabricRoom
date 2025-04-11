from FabricRoom.settings import *
import environ

# Load the Env  ironment vars from FabricRoom/.env
env = environ.Env()
environ.Env.read_env()

DEBUG = False
SECRET_KEY = env("SECRET_KEY")
# SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# SECURE_HSTS_SECONDS = 3600
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True
ALLOWED_HOSTS = ["60hz.dev", "127.0.0.1", "localhost"]


DATABASES = {
    # 'test': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': BASE_DIR / 'db.sqlite3',
    # },
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": env("DATABASE_NAME"),
        "USER": env("DATABASE_USER"),
        "PASSWORD": env("DATABASE_PASSWORD"),
        "HOST": env("DATABASE_HOST"),
        "PORT": env("DATABASE_PORT"),
    }
}

# template dirs not working on this droplet.
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
            BASE_DIR / "main/templates/main",
            # BASE_DIR / 'blog/templates/blog',
            BASE_DIR / "healthstats/templates/healthstats",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.media",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

STATIC_ROOT = BASE_DIR / "static"


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "django": {
            "format": "django: %(message)s",
        },
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "formatter": "verbose",
            "filename": "debug.log",
        },
        # "syslog": {
        #     "level": "DEBUG",
        #     "class": "logging.handlers.SysLogHandler",
        #     "facility": "user",
        #     "formatter": "django",
        #     "address": "/dev/log",
        # },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "DEBUG",
            "propagate": True,
            # 'format': 'django: %(meassage)s'
        },
    },
}
