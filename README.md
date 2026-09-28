# UnifiedLab · Integración inicial

UnifiedLab reúne en un portal los proyectos **DataCenter**, **PhysicLab** y **Química/StellarLab**, preservando sus carpetas y bases de datos originales.

## Estado real de esta entrega

- Portal central Flask con registro, login, logout y dashboard.
- Contraseñas del portal almacenadas mediante hash en `portal/portal_users.db`.
- DataCenter preservado y lanzable en `:5000`.
- PhysicLab preservado y lanzable en `:5001` mediante `run_physics.py`.
- Química/StellarLab preservado en `/Quimica`, todavía sin rutas web integradas.
- **El inicio de sesión del portal aún no es SSO**: DataCenter y PhysicLab conservan sus propios sistemas de autenticación. Esto evita alterar las cuentas, roles e historiales existentes en esta primera fase.

## Requisitos

Python 3.11+ recomendado. Instala las dependencias desde la raíz:

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Inicio

- Windows: ejecuta `INICIAR_WINDOWS.bat`.
- Linux: `./INICIAR_LINUX.sh`.
- Manual: abre tres terminales desde esta carpeta:

```bash
python run_portal.py
```

```bash
cd datacenter_original && python main.py
```

```bash
python run_physics.py
```

Portal: http://127.0.0.1:8000
DataCenter: http://127.0.0.1:5000
PhysicLab: http://127.0.0.1:5001

Crea primero una cuenta en el portal. Las apps heredadas pueden pedir su propia cuenta. No expongas estos servicios a Internet sin revisar secretos, cookies, depuración, permisos y configuración de despliegue.

## Próxima fase recomendada

1. Unificar autenticación mediante una capa de identidad compartida, con migración controlada de roles y cuentas.
2. Integrar DataCenter y PhysicLab bajo prefijos de ruta o Blueprints, resolviendo colisiones y rutas estáticas.
3. Implementar las rutas POST/GET de StellarLab, validar los formularios y enlazar la simulación orbital.
4. Homogeneizar navegación, auditoría y permisos de los tres módulos.

Las bases de datos incluidas son copias de la copia de seguridad recibida. Conserva el ZIP original sin modificar.
