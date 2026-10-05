# Migración de UnifiedLab a MySQL

La versión actual de UnifiedLab utiliza MySQL como almacenamiento operativo. Los SQLite incluidos se conservan como copia de seguridad y como fuente para la migración de los datos existentes.

## 1. Crear bases y tablas

Abre MySQL Workbench conectado como `root` y ejecuta **todo** `mysql_setup.sql`. El script crea:

- `unifiedlab.users`
- `physiclab.users`
- `physiclab.history`
- `datacenter.users`
- `datacenter.audit_log`
- `stellarlab.stars`
- `stellarlab.planets`

Después de ejecutarlo, pulsa el icono de refrescar de `SCHEMAS`.

## 2. Migrar los datos existentes

El ZIP incluye estos SQLite originales:

- `portal/portal_users.db`
- `PhysicLab/physiclab_users.db`
- `datacenter_original/database/users.db`
- `portal/stellar_lab.db`

En CMD, desde la carpeta raíz de UnifiedLab:

```cmd
set MYSQL_HOST=127.0.0.1
set MYSQL_PORT=3306
set MYSQL_USER=unifiedlab
set MYSQL_PASSWORD=LA_CONTRASEÑA_DEL_USUARIO_UNIFIEDLAB
python migrar_sqlite_a_mysql.py
```

Si `MYSQL_PASSWORD` no está definida, el script la solicitará de forma interactiva.

La migración utiliza `INSERT IGNORE`, por lo que puede ejecutarse de nuevo sin duplicar las filas que ya tengan el mismo `id`. No modifica ni elimina los SQLite originales.

## 3. Configurar la aplicación

Variables recomendadas:

```text
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=unifiedlab
MYSQL_PASSWORD=LA_CONTRASEÑA_DEL_USUARIO_UNIFIEDLAB
MYSQL_DATABASE_PORTAL=unifiedlab
MYSQL_DATABASE_PHYSICLAB=physiclab
MYSQL_DATABASE_DATACENTER=datacenter
MYSQL_DATABASE_STELLAR=stellarlab
```

Para producción, usa una contraseña propia y una clave secreta fuerte.

## 4. Comprobar las tablas en Workbench

```sql
USE unifiedlab;
SHOW TABLES;

USE physiclab;
SHOW TABLES;

USE datacenter;
SHOW TABLES;

USE stellarlab;
SHOW TABLES;
```

## 5. Importante

No expongas el puerto 3306 directamente a Internet. Si Workbench se conecta desde otro equipo del laboratorio, limita el acceso a la red de administración.
