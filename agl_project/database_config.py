"""
Configuración de base de datos para producción con MySQL.
Utiliza variables de entorno para credenciales seguras.
"""
import os
from decouple import config

# Configuración de base de datos MySQL/MariaDB
DATABASES_MYSQL = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME', default='agl_db'),
        'USER': config('DB_USER', default='JaviSala23'),
        'PASSWORD': config('DB_PASSWORD', default='Celeste14'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'use_unicode': True,
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'autocommit': True,
        },
        'TEST': {
            'CHARSET': 'utf8mb4',
            'COLLATION': 'utf8mb4_unicode_ci',
        }
    }
}

# Configuración de base de datos SQLite para desarrollo/testing
DATABASES_SQLITE = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'db.sqlite3'),
    }
}

# Seleccionar base de datos según ambiente
USE_MYSQL = config('USE_MYSQL', default=False, cast=bool)

if USE_MYSQL:
    DATABASES = DATABASES_MYSQL
    print("🗄️ Usando MySQL/MariaDB")
else:
    DATABASES = DATABASES_SQLITE
    print("🗄️ Usando SQLite (desarrollo)")

# Configuraciones adicionales para MySQL en producción
if USE_MYSQL:
    # Configuración de conexiones
    DATABASES['default']['CONN_MAX_AGE'] = 60
    DATABASES['default']['CONN_HEALTH_CHECKS'] = True
    
    # Pool de conexiones (opcional, requiere django-mysql)
    # DATABASES['default']['OPTIONS']['pool_name'] = 'agl_pool'
    # DATABASES['default']['OPTIONS']['pool_size'] = 10