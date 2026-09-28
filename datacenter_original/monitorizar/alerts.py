from datetime import datetime


class AlertManager:

    def __init__(self):
        self.previous_status = {}
        self.status_start_time = {}
        self.alerts = []

        self.WARNING_DELAY = 3
        self.CRITICAL_DELAY = 5

    def check_server(self, server):

        current_status = server.status

        previous_status = self.previous_status.get(
            server.name,
            "ONLINE"
        )

        now = datetime.now()

        # El estado acaba de cambiar
        if current_status != previous_status:

            self.status_start_time[server.name] = now

        # Tiempo que lleva en el estado actual
        start_time = self.status_start_time.get(
            server.name,
            now
        )

        duration = (
            now - start_time
        ).total_seconds()


        # WARNING
        if current_status == "WARNING":

            if duration >= self.WARNING_DELAY:

                if previous_status != "WARNING_ALERTED":

                    self.create_alert(
                        server,
                        "WARNING",
                        f"Server {server.name} "
                        f"has remained in WARNING state "
                        f"for {duration:.1f} seconds"
                    )

                    self.previous_status[
                        server.name
                    ] = "WARNING_ALERTED"

                    return


        # CRITICAL
        elif current_status == "CRITICAL":

            if duration >= self.CRITICAL_DELAY:

                if previous_status != "CRITICAL_ALERTED":

                    self.create_alert(
                        server,
                        "CRITICAL",
                        f"Server {server.name} "
                        f"has remained in CRITICAL state "
                        f"for {duration:.1f} seconds"
                    )

                    self.previous_status[
                        server.name
                    ] = "CRITICAL_ALERTED"

                    return


        # ONLINE / RECOVERY
        elif current_status == "ONLINE":

            if previous_status in (
                "WARNING_ALERTED",
                "CRITICAL_ALERTED"
            ):

                self.create_alert(
                    server,
                    "RECOVERY",
                    f"Server {server.name} recovered"
                )

            self.status_start_time.pop(
                server.name,
                None
            )


        self.previous_status[
            server.name
        ] = current_status


    def check_device(self, device):

        current_status = device.status

        previous_status = self.previous_status.get(
            device.name,
            "ONLINE"
        )

        now = datetime.now()

        if current_status != previous_status:

            self.status_start_time[device.name] = now


        start_time = self.status_start_time.get(
            device.name,
            now
        )

        duration = (
            now - start_time
        ).total_seconds()


        if current_status == "WARNING":

            if duration >= self.WARNING_DELAY:

                if previous_status != "WARNING_ALERTED":

                    self.create_device_alert(
                        device,
                        "WARNING",
                        f"Device {device.name} "
                        f"has remained in WARNING "
                        f"for {duration:.1f} seconds"
                    )

                    self.previous_status[
                        device.name
                    ] = "WARNING_ALERTED"

                    return


        elif current_status == "CRITICAL":

            if duration >= self.CRITICAL_DELAY:

                if previous_status != "CRITICAL_ALERTED":

                    self.create_device_alert(
                        device,
                        "CRITICAL",
                        f"Device {device.name} "
                        f"has remained in CRITICAL "
                        f"for {duration:.1f} seconds"
                    )

                    self.previous_status[
                        device.name
                    ] = "CRITICAL_ALERTED"

                    return


        elif current_status == "ONLINE":

            if previous_status in (
                "WARNING_ALERTED",
                "CRITICAL_ALERTED"
            ):

                self.create_device_alert(
                    device,
                    "RECOVERY",
                    f"Device {device.name} recovered"
                )

            self.status_start_time.pop(
                device.name,
                None
            )


        self.previous_status[
            device.name
        ] = current_status


    def create_alert(self, server, severity, message):

        alert = {
            "timestamp": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "rack": server.rack.name,
            "server": server.name,
            "severity": severity,
            "message": message,
            "cpu": server.cpu_usage,
            "temperature": server.temperature
        }

        self.alerts.append(alert)


    def create_device_alert(
        self,
        device,
        severity,
        message
    ):

        alert = {
            "timestamp": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "rack": device.rack.name,
            "device": device.name,
            "severity": severity,
            "message": message,
            "traffic": device.traffic_usage,
            "temperature": device.temperature
        }

        self.alerts.append(alert)


    def get_alerts(self):

        return self.alerts

    def check_switch_ports(self, switch):

        for port, server in switch.connections.items():

            usage = switch.port_usage.get(
                port,
                0
            )

            current_status = switch.get_port_status(
                port
            )

            device_id = (
                f"{switch.name}-PORT-{port}"
            )

            previous_status = self.previous_status.get(
                device_id,
                "ONLINE"
            )

            now = datetime.now()

            # El estado del puerto acaba de cambiar
            if current_status != previous_status:

                self.status_start_time[device_id] = now

            # Tiempo que lleva en el estado actual
            start_time = self.status_start_time.get(
                device_id,
                now
            )

            duration = (
                now - start_time
            ).total_seconds()


            # WARNING
            if current_status == "WARNING":

                if duration >= self.WARNING_DELAY:

                    if previous_status != "WARNING_ALERTED":

                        self.create_port_alert(
                            switch,
                            server,
                            port,
                            "WARNING",
                            usage
                        )

                        self.previous_status[
                            device_id
                        ] = "WARNING_ALERTED"

                        return


            # CRITICAL
            elif current_status == "CRITICAL":

                if duration >= self.CRITICAL_DELAY:

                    if previous_status != "CRITICAL_ALERTED":

                        self.create_port_alert(
                            switch,
                            server,
                            port,
                            "CRITICAL",
                            usage
                        )

                        self.previous_status[
                            device_id
                        ] = "CRITICAL_ALERTED"

                        return


            # ONLINE / RECOVERY
            elif current_status == "ONLINE":

                if previous_status in (
                    "WARNING_ALERTED",
                    "CRITICAL_ALERTED"
                ):

                    self.create_port_alert(
                        switch,
                        server,
                        port,
                        "RECOVERY",
                        usage
                    )

                self.status_start_time.pop(
                    device_id,
                    None
                )


            self.previous_status[
                device_id
            ] = current_status
                
    def create_port_alert(
        self,
        switch,
        server,
        port,
        severity,
        usage
    ):

        alert = {
            "timestamp": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "rack": switch.rack.name,
            "device": switch.name,
            "server": server.name,
            "port": port,
            "severity": severity,
            "message": (
                f"{switch.name} PORT {port} "
                f"({server.name}) "
                f"network utilization: "
                f"{usage:.1f}%"
            ),
            "traffic": usage,
            "temperature": switch.temperature
        }

        self.alerts.append(alert)

    def check_router_ports(self, router):

        for port, device in router.connections.items():

            usage = router.port_usage.get(
                port,
                0
            )

            current_status = router.get_port_status(
                port
            )

            device_id = (
                f"{router.name}-PORT-{port}"
            )

            previous_status = self.previous_status.get(
                device_id,
                "ONLINE"
            )

            now = datetime.now()

            # El estado acaba de cambiar
            if current_status != previous_status:

                self.status_start_time[device_id] = now

            # Tiempo en el estado actual
            start_time = self.status_start_time.get(
                device_id,
                now
            )

            duration = (
                now - start_time
            ).total_seconds()


            # WARNING
            if current_status == "WARNING":

                if duration >= self.WARNING_DELAY:

                    if previous_status != "WARNING_ALERTED":

                        self.create_router_port_alert(
                            router,
                            device,
                            port,
                            "WARNING",
                            usage
                        )

                        self.previous_status[
                            device_id
                        ] = "WARNING_ALERTED"

                        continue


            # CRITICAL
            elif current_status == "CRITICAL":

                if duration >= self.CRITICAL_DELAY:

                    if previous_status != "CRITICAL_ALERTED":

                        self.create_router_port_alert(
                            router,
                            device,
                            port,
                            "CRITICAL",
                            usage
                        )

                        self.previous_status[
                            device_id
                        ] = "CRITICAL_ALERTED"

                        continue


            # ONLINE / RECOVERY
            elif current_status == "ONLINE":

                if previous_status in (
                    "WARNING_ALERTED",
                    "CRITICAL_ALERTED"
                ):

                    self.create_router_port_alert(
                        router,
                        device,
                        port,
                        "RECOVERY",
                        usage
                    )

                self.status_start_time.pop(
                    device_id,
                    None
                )


            self.previous_status[
                device_id
            ] = current_status

    def create_router_port_alert(
        self,
        router,
        device,
        port,
        severity,
        usage
    ):

        alert = {
            "timestamp": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "rack": router.rack.name,
            "device": router.name,
            "connected_device": device.name,
            "port": port,
            "severity": severity,
            "message": (
                f"{router.name} PORT {port} "
                f"({device.name}) "
                f"network utilization: "
                f"{usage:.1f}%"
            ),
            "traffic": usage,
            "temperature": router.temperature
        }

        self.alerts.append(alert)