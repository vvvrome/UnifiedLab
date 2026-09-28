class Router:

    def __init__(self, name, ports=8):

        self.name = name
        self.ports = ports
        self.zone = None

        self.connections = {}
        self.port_usage = {}

        self.status = "ONLINE"

        self.traffic_usage = 0
        self.temperature = 30
        self.power_consumption = 80

    def connect_device(self, device, port):

        if port < 1 or port > self.ports:
            raise ValueError(
                f"Port {port} does not exist on {self.name}"
            )

        if port in self.connections:
            raise ValueError(
                f"Port {port} is already in use"
            )

        self.connections[port] = device
        self.port_usage[port] = device.traffic_usage

        print(
            f"{device.name} connected to "
            f"{self.name} port {port}"
        )

    def disconnect_device(self, port):

        if port in self.connections:
            del self.connections[port]
            if port in self.port_usage:
                del self.port_usage[port]

    def get_used_ports(self):

        return len(self.connections)

    def get_available_ports(self):

        return self.ports - self.get_used_ports()

    def update(self):

        if not self.connections:

            self.traffic_usage = 0

        else:

            total_traffic = 0

            for port, device in self.connections.items():

                usage = device.traffic_usage

                self.port_usage[port] = usage

                total_traffic += usage

            self.traffic_usage = (
                total_traffic / len(self.connections)
            )

        self.temperature = 30 + (
            self.traffic_usage * 0.35
        )

        self.power_consumption = 80 + (
            self.traffic_usage * 1.2
        )

        self.update_status()

    def update_status(self):

        if (
            self.traffic_usage >= 90
            or self.temperature >= 70
        ):

            self.status = "CRITICAL"

        elif (
            self.traffic_usage >= 75
            or self.temperature >= 55
        ):

            self.status = "WARNING"

        else:

            self.status = "ONLINE"

    def get_port_status(self, port):

        usage = self.port_usage.get(
            port,
            0
        )

        if usage >= 90:
            return "CRITICAL"

        elif usage >= 75:
            return "WARNING"

        else:
            return "ONLINE"

    def get_ports_status(self):

        ports = []

        for port, device in self.connections.items():

            usage = self.port_usage.get(
                port,
                0
            )

            ports.append({
                "port": port,
                "device": device.name,
                "usage": usage,
                "status": self.get_port_status(port)
            })

        return ports