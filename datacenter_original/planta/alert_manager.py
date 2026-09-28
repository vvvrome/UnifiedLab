from collections import deque
from datetime import datetime


class PlantAlertManager:

    def __init__(self, max_alerts=200):

        self.alerts = deque(
            maxlen=max_alerts
        )


    def add_alert(
        self,
        severity,
        message,
        device=None,
        parameter=None,
        value=None
    ):

        alert = {

            "timestamp":
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),

            "severity":
                severity,

            "message":
                message,

            "device":
                device,

            "parameter":
                parameter,

            "value":
                value

        }


        self.alerts.append(alert)


    def get_alerts(self):

        return list(self.alerts)


    def clear(self):

        self.alerts.clear()