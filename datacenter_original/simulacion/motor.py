import time
from simulacion.workload import WorkloadGenerator
from monitorizar.alerts import AlertManager
from seguridad.security_manager import SecurityManager
from planta.proceso import NuclearPlant

class SimulationEngine:

    def __init__(self, datacenter, config):
        self.datacenter = datacenter
        self.workload = WorkloadGenerator()
        self.alert_manager = AlertManager()
        self.security_manager = SecurityManager()
        self.plant = NuclearPlant(
            config.get("faults", {})
        )
        self.tick = 0

    def update(self):

        self.tick += 1
        self.plant.update()

        for rack in self.datacenter.racks:

            for server in rack.servers:

                self.workload.generate(server)

                server.update()

                self.alert_manager.check_server(server)

            for switch in rack.switches:
                switch.update()
                self.alert_manager.check_device(switch)
                self.alert_manager.check_switch_ports(switch)

            for router in rack.routers:
                router.update()

                self.alert_manager.check_device(router)
                self.alert_manager.check_router_ports(router)
                
    def run(self, ticks, delay=1):
        for _ in range(ticks):
            self.update()

            print(f"\n--- TICK {self.tick} ---")
            print(self.datacenter)

            time.sleep(delay)