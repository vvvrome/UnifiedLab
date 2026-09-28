# StellarLab integrado en UnifiedLab

StellarLab es el módulo de astrofísica y química de UnifiedLab. Está conectado al portal Flask mediante un Blueprint y utiliza la misma sesión de usuario.

## Rutas

- `/stellar/` panel del laboratorio
- `/stellar/estrella` creación y análisis de estrellas
- `/stellar/planeta` creación de planetas
- `/stellar/orbita` simulación gravitatoria

Los datos de estrellas y planetas se almacenan por usuario en `portal/stellar_lab.db`.

La validación del servidor comprueba los símbolos químicos contra `elements.json` y que las composiciones sumen 100 %.
