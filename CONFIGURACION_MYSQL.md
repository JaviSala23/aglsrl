# 🗄️ Configuración MySQL para AGL SRL

## Comandos SQL a ejecutar

Abre MySQL como root con:
```bash
sudo mysql -u root
```

Luego ejecuta estos comandos SQL:

```sql
-- 1. Crear la base de datos
CREATE DATABASE IF NOT EXISTS agl_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- 2. Crear usuario para la aplicación
CREATE USER IF NOT EXISTS 'agl_user'@'localhost' 
IDENTIFIED BY 'agl_password_2024';

-- 3. Otorgar todos los permisos sobre la base de datos
GRANT ALL PRIVILEGES ON agl_db.* TO 'agl_user'@'localhost';

-- 4. Aplicar cambios
FLUSH PRIVILEGES;

-- 5. Verificar que todo se creó correctamente
SHOW DATABASES LIKE 'agl_db';
SELECT User, Host FROM mysql.user WHERE User = 'agl_user';

-- 6. Usar la base de datos
USE agl_db;

-- 7. Mostrar información de la BD
SELECT DATABASE(), @@character_set_database, @@collation_database;

-- 8. Salir
EXIT;
```

## Comandos Django después de configurar MySQL

Una vez ejecutados los comandos SQL, ejecuta:

```bash
# 1. Verificar conexión
python manage.py check --database default

# 2. Crear migraciones para MySQL
python manage.py migrate

# 3. Cargar datos maestros
python manage.py cargar_datos_maestros

# 4. Crear cuentas de ejemplo
python manage.py crear_cuentas_ejemplo

# 5. Crear superusuario para MySQL
python manage.py createsuperuser

# 6. Ejecutar servidor
python manage.py runserver
```

## Verificación de la configuración

El archivo `.env` ya está configurado con:
- `USE_MYSQL=True` 
- Credenciales de la base de datos
- Configuraciones de Django

Una vez que ejecutes los comandos SQL, Django se conectará automáticamente a MySQL.

---

**¿Ya ejecutaste los comandos SQL en MySQL?** Si es así, puedo continuar con la migración de datos.