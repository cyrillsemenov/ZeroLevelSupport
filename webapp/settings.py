"""
Django settings for webapp project.

Generated by 'django-admin startproject' using Django 5.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import os
import secrets
from pathlib import Path
from typing import Literal

from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode

PROJECT_NAME = "ZeroLevelSupport"
PROJECT_DESCRIPTION = "Question answering bot"
PROJECT_VERSION = "0.0.0"

BOT_API_KEY = os.environ["BOT_API_KEY"]
BOT_SKIP_UPDATES = os.getenv("BOT_SKIP_UPDATES", True)

link_preview: Literal["large", "small", "disable"] = os.getenv(
    "BOT_LINK_PREVIEW", "large"
)
BOT_PROPERTIES = DefaultBotProperties(
    parse_mode=os.getenv("BOT_PARSE_MODE", ParseMode.HTML.value),
    disable_notification=os.getenv("BOT_DISABLE_NOTIFICATION"),
    protect_content=os.getenv("BOT_PROTECT_CONTENT"),
    allow_sending_without_reply=os.getenv("BOT_SEND_WITHOUT_REPLY"),
    link_preview_is_disabled=(link_preview == "disable"),
    link_preview_prefer_small_media=(link_preview == "small"),
    link_preview_prefer_large_media=(link_preview == "large"),
    link_preview_show_above_text=os.getenv("BOT_LINK_PREVIEW_ABOVE_TEXT"),
)

WEBHOOK_SECRET = secrets.token_urlsafe(32)
WEBHOOK_PATH = "/bot/{bot_token}"
WEBHOOK_URL = f"https://a9c5-78-58-238-159.ngrok-free.app/api/bot/{BOT_API_KEY}"

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

SECRET_KEY = os.environ.get("SECRET_KEY")
DEBUG = bool(os.environ.get("DEBUG", default=0))
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", default="").split(" ")


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "telegram_bot",
    "question_app",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "webapp.urls"

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
            ],
        },
    },
]

WSGI_APPLICATION = "webapp.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': os.path.join(BASE_DIR, "db.sqlite3"),
    # }
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "mydatabase"),
        "USER": os.getenv("POSTGRES_USER", "myuser"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "mypassword"),
        "HOST": os.getenv("DB_HOST", "mydatabase"),
        "PORT": os.getenv("DB_PORT", "mydatabase"),
    },
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "/staticfiles/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
