class Switch:

    def __init__(self, name, ports=48):

        self.name = name
        self.ports = ports
        self.zone = None

        self.connections = {}
        self.port_usage = {}

        self.status = "ONLINE"

        self.traffic_usage = 0
        self.temperature = 25
        self.power_consumption = 50

    def connect_server(self, server, port):

        if port < 1 or port > self.ports:
            raise ValueError(
                f"Port {port} does not exist on {self.name}"
            )

        if port in self.connections:
            raise ValueError(
                f"Port {port} is already in use"
            )

        self.connections[port] = server
        self.port_usage[port]= 0

        server.switch = self.name
        server.switch_port = port

        print(
            f"{server.name} connected to "
            f"{self.name} port {port}"
        )

    def disconnect_server(self, port):

        if port in self.connections:

            server = self.connections[port]

            server.switch = None
            server.switch_port = None

            del self.connections[port]

        if port in self.port_usage:
            del self.connections[port]
        

    def get_used_ports(self):

        return len(self.connections)

    def get_available_ports(self):

        return self.ports - self.get_used_ports()

    def get_port_usage(self, port):
        return self.port_usage.get(
            port,
            0
        )

    def get_ports_status(self):

        ports = []

        for port, server in self.connections.items():

            usage = self.port_usage.get(
                port,
                0
            )

            ports.append({
                "port": port,
                "server": server.name,
                "usage": usage,
                "status": self.get_port_status(port)
            })

        return ports

    def update(self):

        if not self.connections:

            self.traffic_usage = 0

        else:

            total_network = 0

            for port, server in self.connections.items():

                usage = server.network_usage

                self.port_usage[port] = usage

                total_network += usage

            self.traffic_usage = (
                total_network / len(self.connections)
            )

        self.temperature = 25 + (
            self.traffic_usage * 0.4
        )

        self.power_consumption = 50 + (
            self.traffic_usage * 1.5
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

        usage = self.port_usage.get(port, 0)

        if usage >= 90:
            return "CRITICAL"

        elif usage >= 75:
            return "WARNING"

        else:
            return "ONLINE"