from datetime import datetime


class SecurityController:

    def __init__(self, alert_manager):
        self.alert_manager = alert_manager

        self.status = "NORMAL"
        self.channel_status = "SECURE"
        self.last_action = "System initialized"
        self.last_event = None

    def handle_qkd_result(self, result):
        status = result.get("status", "UNKNOWN")

        if status == "COMPROMISED":
            self._handle_compromise(result)

        elif status == "SECURE":
            self._handle_secure(result)

        return self.get_state()

    def _handle_compromise(self, result):

        self.status = "CRITICAL"
        self.channel_status = "ISOLATED"
        self.last_action = "QKD channel isolated"
        self.last_event = datetime.now().strftime("%H:%M:%S")

        qber = result.get("qber_percent", 0)

        self.alert_manager.add_alert(
            severity="CRITICAL",
            message="QKD channel isolated after interception detection",
            device="QKD-01",
            parameter="QBER",
            value=qber
        )

        self.alert_manager.add_alert(
            severity="WARNING",
            message="Communication mode switched to restricted",
            device="SECURITY-CTRL-01",
            parameter="CHANNEL",
            value="ISOLATED"
        )

    def _handle_secure(self, result):

        if self.channel_status == "ISOLATED":

            self.status = "RECOVERING"
            self.channel_status = "SECURE"
            self.last_action = "QKD channel restored"
            self.last_event = datetime.now().strftime("%H:%M:%S")

            self.alert_manager.add_alert(
                severity="INFO",
                message="QKD channel restored after successful verification",
                device="QKD-01",
                parameter="CHANNEL",
                value="SECURE"
            )

            self.status = "NORMAL"

        else:
            self.status = "NORMAL"
            self.channel_status = "SECURE"
            self.last_action = "Secure QKD session established"

    def get_state(self):

        return {
            "status": self.status,
            "channel_status": self.channel_status,
            "last_action": self.last_action,
            "last_event": self.last_event
        }