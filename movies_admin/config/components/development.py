from config.components.common import INSTALLED_APPS, MIDDLEWARE

ALLOWED_HOSTS = (
    "localhost",
    "127.0.0.1",
    "[::1]",
)
INTERNAL_IPS = (
    "localhost",
    "127.0.0.1",
    "[::1]",
)
INSTALLED_APPS += (
    "debug_toolbar",
    "django_extensions",
    "corsheaders",
)
MIDDLEWARE = (
    ("corsheaders.middleware.CorsMiddleware",)
    + MIDDLEWARE
    + ("debug_toolbar.middleware.DebugToolbarMiddleware",)
)
CORS_ALLOWED_ORIGINS = ("http://127.0.0.1:8080",)
