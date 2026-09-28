from infraestructura.rack import Rack
from infraestructura.server import Server


class DataCenter:
    def __init__(self, name):
        self.name = name
        self.racks = []

    def add_rack(self, rack):
        self.racks.append(rack)

    def __str__(self):
        result = f"DataCenter: {self.name}\n"

        for rack in self.racks:
            result += f"  {rack}\n"

        return result

    @classmethod
    def from_config(cls, config):
        datacenter = cls(config["name"])

        for rack_config in config["racks"]:
            rack = Rack(
                rack_config["name"],
                rack_config["total_units"]
            )

            for server_config in rack_config["servers"]:
                server = Server(
                    name=server_config["name"],
                    cpu=server_config["cpu"],
                    ram=server_config["ram"],
                    storage=server_config["storage"],
                    rack_units=server_config["rack_units"],
                    server_type=server_config["type"]
                )

                rack.add_server(server)

            datacenter.add_rack(rack)

        return datacenter