-- Script SQL para crear la base de datos AGL
-- Ejecutar como usuario JaviSala23

-- 1. Crear la base de datos si no existe
CREATE DATABASE IF NOT EXISTS agl_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- 2. Usar la base de datos
USE agl_db;

-- 3. Verificar la base de datos creada
SELECT DATABASE() as 'Base_de_Datos_Actual';
SELECT @@character_set_database as 'Charset', @@collation_database as 'Collation';

-- 4. Mostrar información del usuario actual
SELECT USER() as 'Usuario_Actual', CONNECTION_ID() as 'ID_Conexion';

-- 5. Verificar permisos en la base de datos
SHOW GRANTS FOR CURRENT_USER();

-- Comentarios:
-- - La base de datos se llama 'agl_db'
-- - Usa charset utf8mb4 para soporte completo de Unicode
-- - El usuario JaviSala23 debe tener permisos de administrador o propietario de la BD