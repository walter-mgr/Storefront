import os
import dj_database_url
from .common import *

DEBUG = False

SECRET_KEY = os.environ["SECRET_KEY"]

ALLOWED_HOSTS = ["buy-store-prod-17b181031b24.herokuapp.com"]

DATABASE_URL = os.environ["HEROKU_POSTGRESQL_PINK_URL"]

DATABASES = {"default": dj_database_url.config()}

REDIS_URL = os.environ["REDIS_URL"]

CELERY_BROKER_URL = REDIS_URL  # Replace with your Redis URL

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "TIMEOUT": 10 * 60,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

EMAIL_HOST = os.environ["MAILGUN_SMTP_SERVER"]
EMAIL_HOST_USER = os.environ["MAILGUN_SMTP_LOGIN"]
EMAIL_HOST_PASSWORD = os.environ["MAILGUN_SMTP_PASSWORD"]
EMAIL_PORT = os.environ["MAILGUN_SMTP_PORT"]
