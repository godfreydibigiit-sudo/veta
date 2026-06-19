"""
Django settings for VETA Hotel Booking System.
"""
import os
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-in-production-@veta2026')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost').split(',')

# Application definition
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'crispy_forms',
    # 'crispy_bootstrap5',
    
    # Local apps
    'apps.core',
    'apps.users',
    'apps.rooms',
    'apps.bookings',
    'apps.dashboard',
]

# ============================================
# JAZZMIN SETTINGS - VETA Hotel Premium Admin
# ============================================

JAZZMIN_SETTINGS = {
    # Branding
    "site_title": "VETA Hotel | Admin",
    "site_header": "VETA Hotel",
    "site_brand": "VETA Hotel",
    "site_logo": None,
    "site_logo_classes": "elevation-3",
    "site_icon": None,
    
    # Welcome
    "welcome_sign": "Welcome to VETA Hotel Management System",
    
    # Copyright
    "copyright": f"© {__import__('datetime').datetime.now().year} VETA Hotel. All rights reserved.",
    
    # Search
    "search_model": ["users.User", "bookings.Booking", "rooms.Room"],
    
    # Top Menu
    "topmenu_links": [
        {"name": "Dashboard", "url": "admin:index", "icon": "fas fa-tachometer-alt"},
        {"name": "View Site", "url": "home", "new_window": True, "icon": "fas fa-external-link-alt"},
        {"name": "Bookings", "model": "bookings.Booking", "icon": "fas fa-calendar-check"},
        {"name": "Rooms", "model": "rooms.Room", "icon": "fas fa-door-open"},
        {"name": "Users", "model": "users.User", "icon": "fas fa-users"},
    ],
    
    # User Menu
    "usermenu_links": [
        {"name": "View Website", "url": "home", "new_window": True, "icon": "fas fa-globe"},
        {"model": "auth.user"},
        {"name": "Support", "url": "#", "icon": "fas fa-headset"},
    ],
    
    # Sidebar
    "show_sidebar": True,
    "navigation_expanded": False,
    
    # Apps to hide
    "hide_apps": [],
    "hide_models": [],
    
    # Order
    "order_with_respect_to": [
        "users", "users.User", "users.StaffProfile",
        "rooms", "rooms.Room", "rooms.RoomType", "rooms.RoomImage",
        "bookings", "bookings.Booking",
        "core", "core.AuditLog",
        "auth", "auth.Group",
    ],
    
    # Custom links in sidebar
    "custom_links": {
        "users": [{
            "name": "Add Staff Member",
            "url": "admin:users_user_add",
            "icon": "fas fa-user-plus",
            "permissions": ["users.add_user"]
        }],
        "rooms": [{
            "name": "View All Rooms",
            "url": "rooms:staff_list",
            "icon": "fas fa-list",
            "new_window": True
        }],
    },
    
    # Icons - Professional Set
    "icons": {
        # Auth
        "auth": "fas fa-shield-alt",
        "auth.user": "fas fa-user-shield",
        "auth.group": "fas fa-layer-group",
        
        # Users
        "users": "fas fa-users-cog",
        "users.User": "fas fa-user-circle",
        "users.StaffProfile": "fas fa-id-badge",
        
        # Rooms
        "rooms": "fas fa-building",
        "rooms.Room": "fas fa-door-open",
        "rooms.RoomType": "fas fa-layer-group",
        "rooms.RoomImage": "fas fa-images",
        
        # Bookings
        "bookings": "fas fa-calendar-alt",
        "bookings.Booking": "fas fa-calendar-check",
        
        # Core
        "core": "fas fa-cogs",
        "core.AuditLog": "fas fa-clipboard-list",
        
        # Django
        "sites": "fas fa-globe",
        "sessions": "fas fa-clock",
        "contenttypes": "fas fa-cubes",
    },
    
    # Default icons
    "default_icon_parents": "fas fa-folder",
    "default_icon_children": "fas fa-file",
    
    # Related Modal
    "related_modal_active": True,
    
    # Custom CSS/JS
    "custom_css": "css/jazzmin-custom.css",
    "custom_js": "js/jazzmin-custom.js",
    
    # UI Builder
    "show_ui_builder": False,
    
    # Change form
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "users.user": "horizontal_tabs",
        "bookings.booking": "carousel",
    },
    
    # Language
    "language_chooser": False,
}

# ============================================
# JAZZMIN UI TWEAKS - Premium Design
# ============================================

JAZZMIN_UI_TWEAKS = {
    "theme": "flatly",
    
    # Navbar
    "navbar": "navbar-white navbar-light",
    "navbar_small_text": False,
    "navbar_fixed": True,
    "no_navbar_border": True,
    "brand_colour": "navbar-teal",
    "brand_small_text": False,
    
    # Sidebar
    "sidebar": "sidebar-dark-teal",
    "sidebar_nav_small_text": False,
    "sidebar_fixed": True,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": True,
    
    # Body
    "body_small_text": False,
    "accent": "accent-teal",
    "dark_mode_theme": None,
    
    # Layout
    "layout_boxed": False,
    "footer_fixed": False,
    "footer_small_text": False,
    
    # Buttons
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
    
    # Extra
    "actions_sticky_top": True,
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Custom User Model
AUTH_USER_MODEL = 'users.User'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 6}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Authentication Settings
LOGIN_URL = '/account/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Dar_es_Salaam'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Messages Tags
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'secondary',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# Session Settings
SESSION_COOKIE_AGE = 86400  # 24 hours in seconds
SESSION_SAVE_EVERY_REQUEST = True