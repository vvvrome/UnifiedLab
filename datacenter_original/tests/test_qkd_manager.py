from planta.security.qkd_manager import QKDManager


print("================================")
print("       QKD MANAGER TEST")
print("================================")


manager = QKDManager(
    key_length=256,
    qber_threshold=0.11
)


print()
print("----- SESIÓN SEGURA -----")

result = manager.start_session(
    eve=False
)

print(result)


print()
print("¿Existe una clave válida?")

print(
    manager.has_valid_key()
)


print()
print("----- SESIÓN CON EVE -----")

result = manager.start_session(
    eve=True
)

print(result)


print()
print("¿Existe una clave válida?")

print(
    manager.has_valid_key()
)


print()
print("----- HISTORIAL -----")

for session in manager.get_history():

    print(session)

print()
print("================================")
print("       PLANT QKD TEST")
print("================================")

from planta.proceso import NuclearPlant

plant = NuclearPlant()

print()
print("Estado inicial de QKD:")

print(
    plant.qkd_manager.get_status()
)

print()
print("Ejecutando sesión segura:")

print(
    plant.run_qkd_session(
        eve=False
    )
)

print()
print("Ejecutando ataque:")

print(
    plant.run_qkd_session(
        eve=True
    )
)

print()
print("Estado final de QKD:")

print(
    plant.qkd_manager.get_status()
)