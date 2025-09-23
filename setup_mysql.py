#!/usr/bin/env python
"""
Script para probar la conexión a MySQL y crear la base de datos si no existe.
"""
import mysql.connector
from mysql.connector import Error
import sys

def test_mysql_connection():
    """Probar conexión a MySQL y crear base de datos si es necesario."""
    
    # Configuración de conexión
    config = {
        'host': 'localhost',
        'user': 'root',
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci'
    }
    
    try:
        # Conectar como root para crear BD y usuario
        print("🔌 Conectando a MySQL como root...")
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        # Crear base de datos
        print("📊 Creando base de datos 'agl_db'...")
        cursor.execute("CREATE DATABASE IF NOT EXISTS agl_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        
        # Crear usuario
        print("👤 Creando usuario 'agl_user'...")
        cursor.execute("CREATE USER IF NOT EXISTS 'agl_user'@'localhost' IDENTIFIED BY 'agl_password_2024'")
        
        # Otorgar permisos
        print("🔑 Otorgando permisos...")
        cursor.execute("GRANT ALL PRIVILEGES ON agl_db.* TO 'agl_user'@'localhost'")
        cursor.execute("FLUSH PRIVILEGES")
        
        # Verificar
        cursor.execute("SHOW DATABASES LIKE 'agl_db'")
        db_exists = cursor.fetchone()
        
        cursor.execute("SELECT User, Host FROM mysql.user WHERE User = 'agl_user'")
        user_exists = cursor.fetchone()
        
        if db_exists and user_exists:
            print("✅ Base de datos y usuario creados exitosamente!")
            print(f"   📊 Base de datos: {db_exists[0]}")
            print(f"   👤 Usuario: {user_exists[0]}@{user_exists[1]}")
        else:
            print("❌ Error: No se pudieron crear la BD o el usuario")
            return False
        
        cursor.close()
        connection.close()
        
        # Probar conexión con el nuevo usuario
        print("\n🔌 Probando conexión con el usuario de la aplicación...")
        app_config = {
            'host': 'localhost',
            'database': 'agl_db',
            'user': 'agl_user',
            'password': 'agl_password_2024',
            'charset': 'utf8mb4'
        }
        
        app_connection = mysql.connector.connect(**app_config)
        app_cursor = app_connection.cursor()
        
        # Probar una consulta simple
        app_cursor.execute("SELECT DATABASE(), USER(), NOW()")
        result = app_cursor.fetchone()
        
        print("✅ Conexión de aplicación exitosa!")
        print(f"   📊 Base de datos actual: {result[0]}")
        print(f"   👤 Usuario actual: {result[1]}")
        print(f"   🕐 Timestamp: {result[2]}")
        
        app_cursor.close()
        app_connection.close()
        
        return True
        
    except Error as e:
        print(f"❌ Error de MySQL: {e}")
        return False
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False

if __name__ == "__main__":
    print("🗄️ Configurando MySQL para AGL SRL")
    print("=" * 50)
    
    if test_mysql_connection():
        print("\n🎉 ¡Configuración de MySQL completada!")
        print("\n📝 Próximos pasos:")
        print("   1. Ejecutar: python manage.py migrate")
        print("   2. Ejecutar: python manage.py cargar_datos_maestros")
        print("   3. Ejecutar: python manage.py crear_cuentas_ejemplo")
    else:
        print("\n❌ Error en la configuración. Revisa los mensajes anteriores.")
        sys.exit(1)