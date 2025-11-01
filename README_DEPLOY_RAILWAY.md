# Despliegue Django en Railway

## 1. Requisitos en settings.py
- Agrega WhiteNoise y usa variables de entorno:

```python
import os

ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS","127.0.0.1,localhost").split(",") if h.strip()]
CSRF_TRUSTED_ORIGINS = [u.strip() for u in os.getenv("CSRF_TRUSTED_ORIGINS","").split(",") if u.strip()]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # debajo de SecurityMiddleware
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
