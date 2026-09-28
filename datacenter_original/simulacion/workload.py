import random


class WorkloadGenerator:

    def __init__(self, test_mode=False):
        self.test_mode = test_mode

    def generate(self, server):

        if server.server_type == "WEB":

            cpu_change = random.randint(-10, 10)
            ram_change = random.randint(-5, 5)
            network_change = random.randint(-15, 15)

        elif server.server_type == "DATABASE":

            cpu_change = random.randint(-8, 8)
            ram_change = random.randint(-8, 8)
            network_change = random.randint(-8, 8)

        elif server.server_type == "STORAGE":

            cpu_change = random.randint(-5, 5)
            ram_change = random.randint(-5, 5)
            network_change = random.randint(-20, 20)

        elif server.server_type == "BACKUP":

            cpu_change = random.randint(-12, 12)
            ram_change = random.randint(-8, 8)
            network_change = random.randint(-20, 20)

        else:

            cpu_change = random.randint(-8, 8)
            ram_change = random.randint(-5, 5)
            network_change = random.randint(-10, 10)


        new_cpu = max(
            0,
            min(100, server.cpu_usage + cpu_change)
        )

        new_ram = max(
            0,
            min(100, server.ram_usage + ram_change)
        )

        new_network = max(
            0,
            min(100, server.network_usage + network_change)
        )


        server.set_cpu_usage(new_cpu)
        server.set_ram_usage(new_ram)
        server.set_network_usage(new_network)