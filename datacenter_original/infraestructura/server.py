class Server:
    def __init__(self, name, cpu, ram, storage, rack_units, server_type="GENERIC"):
        
        self.name = name
        self.cpu = cpu
        self.ram = ram
        self.storage = storage
        self.rack_units = rack_units
        self.server_type = server_type
        self.switch = None
        self.switch_port = None
        self.zone = None

        self.status = "online"

        self.cpu_usage = 0
        self.ram_usage = 0
        self.network_usage = 0
        self.temperature = 20
        self.power_consumption = 0

    def __str__(self):
        return (
            f"Server: {self.name}\n"
            f"        Status: {self.status}\n"
            f"        CPU: {self.cpu_usage}%\n"
            f"        RAM: {self.ram_usage}%\n"
            f"        Network: {self.network_usage}%\n"
            f"        Temperature: {self.temperature} °C\n"
            f"        Power: {self.power_consumption} W"
        )

    def set_cpu_usage(self, usage):
        if 0 <= usage <= 100:
            self.cpu_usage = usage
        else:
            print("El uso de CPU debe estar entre 0 y 100%")

    def set_ram_usage(self, usage):
        if 0 <= usage <= 100:
            self.ram_usage = usage
        else:
            print("El uso de RAM tiene que estar entre 0 y 100")

    def set_network_usage(self, usage):
        if 0 <= usage <= 100:
            self.network_usage = usage
        else:
            print("El useo de red tiene que estar entre 0 y 100")

    def calculate_power_consumption(self):
        base_power = 100
        max_power = 400

        self.power_consumption = base_power +(
            (max_power - base_power) * self.cpu_usage / 100
        )

    def calculate_temperature(self):
        base_temperature = 20
        max_temperature = 80

        self.temperature = base_temperature + (
            (max_temperature - base_temperature) * self.cpu_usage / 100
        )

    def update(self):
        self.calculate_power_consumption()
        self.calculate_temperature()
        self.update_status()

    def update_status(self):

        if self.status == "OFFLINE":
            return

        if self.temperature >= 80 or self.cpu_usage >= 95:
            self.status = "CRITICAL"

        elif self.temperature >= 70 or self.cpu_usage >= 90:
            self.status = "WARNING"

        else:
            self.status = "ONLINE"
