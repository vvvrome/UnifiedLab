PHYSICLAB: integración de autenticación y rutas

1. Sustituye tu app.py por este archivo.
2. Copia templates/login.html y templates/register.html a tu carpeta templates/.
3. Copia static/css/auth.css a static/css/auth.css.
4. Conserva tus módulos python/Algebra.py, python/Fisica_I.py y tu templates/index.html.
5. Instala dependencias del proyecto (Flask, numpy, sympy, matplotlib y las de tus módulos).
6. Ejecuta: python app.py
7. Entra en /register para crear el primer usuario. Las cuentas se guardan en physiclab_users.db; las contraseñas se almacenan con hash.

Rutas: /login, /register, /logout, /sistemas, /fisica, /resto, /calculo, /ejercicios, /simulador, /laboratorio3d, /historial.
Las rutas de secciones reutilizan index.html y el backend existente, estableciendo active_section según la URL. Para que la navegación visual use estas URLs, actualiza los enlaces del index.html a esas rutas. Los formularios pueden seguir enviando el campo oculto section al endpoint actual.

Seguridad: define PHYSICLAB_SECRET_KEY como variable de entorno antes de desplegar. Esta versión añade autenticación general, pero no convierte aún el historial MySQL existente en historial aislado por usuario. No expongas debug=True en producción.
