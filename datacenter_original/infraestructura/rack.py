class Rack:
    def __init__(self, name, total_units=42):
        self.name = name
        self.total_units = total_units
        self.servers = []
        self.switches = []
        self.routers = []

    def add_server(self, server):
        if self.used_units() + server.rack_units <= self.total_units:
            self.servers.append(server)
            print(f"{server.name} añadido a {self.name}")
        else:
            print(f"No hay espacio sufiiente en {self.name}")

    def __str__(self):
        result = f"Rack: {self.name}\n"

        for server in self.servers:
            result += f"     {server}\n"

        return result

    def used_units(self):
        total = 0

        for server in self.servers:
            total += server.rack_units

        return total

    def available_units(self):
        return self.total_units - self.used_units()

    def add_switches(self, switch):
        self.switches.append(switch)
        print(f"{switch.name} añadido a {self.name}")

    def get_switches(self):
        return self.switches

    def add_router(self, router):
        self.routers.append(router)
        print(f"{router.name} añadido a {self.name}")