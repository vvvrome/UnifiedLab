from getpass import getpass

from users import (
    init_database,
    create_user
)


init_database()

username = input(
    "Usuario administrador: "
).strip()

password = getpass(
    "Contraseña: "
)

success = create_user(
    username,
    password,
    "ADMIN"
)

if success:

    print(
        "Administrador creado correctamente."
    )

else:

    print(
        "Ese usuario ya existe."
    )