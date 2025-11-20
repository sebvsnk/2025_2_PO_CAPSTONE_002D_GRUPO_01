"""
Django settings for backend project (dev).
"""

from pathlib import Path 
import os
import sys  # <--- IMPORTANTE: Necesario para detectar si estamos en modo test
from dotenv import load_dotenv

load_dotenv()  # lee variables desde .env

# --- Paths base ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Básicos ---
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-no-usar-en-prod")
DEBUG = bool(int(os.getenv("DEBUG", "1")))
ALLOWED_HOSTS = ["*"]
LOGIN_URL = "/login"

# --- Apps ---
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework.authtoken",

    # Terceros
    "rest_framework",
    "corsheaders",
    "django_filters",
    
    # 🌟 Nuevo: DRF Spectacular para Swagger/OpenAPI
    "drf_spectacular",

    # Tu app
    "api",
]

# --- Middleware ---
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

ROOT_URLCONF = "backend.urls"

# --- TEMPLATES ---
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Aquí le decimos a Django que busque una carpeta 'templates'
        # en la raíz del proyecto.
        "DIRS": [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = "backend.wsgi.application"

# ---------------------------------------------------------
# --- CONFIGURACIÓN DE BASE DE DATOS (CORREGIDA) ---
# ---------------------------------------------------------

# Detectamos si el comando actual es 'test' (ej: python manage.py test)
TESTING = 'test' in sys.argv

if TESTING:
    # ✅ MODO TEST: Usamos SQLite local
    # Esto evita errores de conexión con Supabase y es mucho más rápido
    print("⚙️  MODO TEST DETECTADO: Usando SQLite local para pruebas...")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

    # Desactiva las migraciones para la app 'api' durante los tests.
    # Esto fuerza a Django a crear las tablas directamente desde los modelos
    # (ideal para modelos con 'managed = False').
    MIGRATION_MODULES = {
        'api': None,
    }
else:
    # 🌍 MODO DEV/PROD: Usamos PostgreSQL (Supabase)
    # Se conecta aquí solo si NO estamos corriendo tests
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("PGDATABASE"),
            "USER": os.getenv("PGUSER"),
            "PASSWORD": os.getenv("PGPASSWORD"),
            "HOST": os.getenv("PGHOST"),
            "PORT": os.getenv("PGPORT", "5432"),
            "OPTIONS": {
                "sslmode": "require",
                "options": "-c search_path=apt,public",
            },
        }
    }

# ---------------------------------------------------------


# --- DRF (CORREGIDO PARA USAR SUPABASE JWT y SPECTACULAR) ---
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        # Le decimos a DRF que use nuestra clase personalizada
        "api.authentication.SupabaseJWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    # 🌟 Nuevo: Usar el generador de esquemas de drf-spectacular
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# ----------------------------------------------------
# --- CONFIGURACIÓN DE SPECTACULAR (SWAGGER/OPENAPI) ---
# ----------------------------------------------------
SPECTACULAR_SETTINGS = {
    # Información general que se mostrará en la interfaz de Swagger
    'TITLE': 'API de Gestión de Taller PepsiCo',
    'DESCRIPTION': 'Documentación de la API Backend para el ingreso de vehículos y seguimiento de OTs.',
    'VERSION': 'v1',
    'SERVE_INCLUDE_SCHEMA': False, # No incluir el archivo JSON del esquema en la respuesta de la UI
    
    # Customización de la Autenticación
    'SECURITY': [
        {
            "BearerAuth": []
        }
    ],
    'COMPONENTS': {
        'securitySchemes': {
            'BearerAuth': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT',
            }
        }
    },
    'ENUM_NAME_OVERRIDES': { # Ayuda a que los enums se vean bien en el schema
        'RolEnum': 'api.models.Usuario.ROL_CHOICES',
    },
}
# ----------------------------------------------------


# --- CORS ---
CORS_ALLOWED_ORIGINS = [
    os.getenv("CORS_ORIGIN", "http://localhost:5173"),
    os.getenv("CORS_ORIGIN_2", "http://127.0.0.1:5173"),
]

# 🌟 1. CORRECCIÓN AÑADIDA: Exponer el encabezado del nombre de archivo
CORS_EXPOSE_HEADERS = [
    'Content-Disposition',
]


# --- Internacionalización / Zona horaria ---
LANGUAGE_CODE = "es-cl"
TIME_ZONE = "America/Santiago"
USE_I18N = True
USE_TZ = True

# --- Archivos estáticos ---
STATIC_URL = "static/"

# Le decimos a Django dónde encontrar nuestra carpeta 'static'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

# --- PK por defecto ---
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"