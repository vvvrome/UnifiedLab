from planta.security.qkd import QKDSession


print("=== QKD SIN ATAQUE ===")

qkd = QKDSession(key_length=256)

result = qkd.run(eve=False)

print(result)


print()
print("=== QKD CON EVE ===")

qkd = QKDSession(key_length=256)

result = qkd.run(eve=True)

print(result)