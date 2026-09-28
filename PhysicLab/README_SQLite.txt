PhysicsLab: cambio de historial MySQL a SQLite

Archivos incluidos:
- app.py: historial almacenado en SQLite, en el mismo archivo de base de datos que las cuentas (physiclab_users.db por defecto).
- index.html: interfaz actualizada para indicar SQLite y no enviar un nombre de usuario editable.

Instalación:
1. Haz una copia de seguridad de tu app.py e index.html actuales.
2. Sustituye ambos por los archivos de este paquete.
3. Mantén la estructura del proyecto: app.py, carpeta templates/index.html y el resto de módulos existentes.
4. Reinicia Flask. La tabla history se crea automáticamente en physiclab_users.db.

No se migra automáticamente ningún registro que estuviera en MySQL. La tabla SQLite empezará a guardar los registros nuevos.
La API ignora cualquier username enviado por el cliente: las cuentas normales solo leen sus registros; admin puede consultar el historial global.
