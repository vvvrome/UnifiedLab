class QuantumIntrusionDetector:

    def __init__(self, qber_threshold=0.11):

        self.qber_threshold = qber_threshold

        self.status = "NORMAL"
        self.last_qber = 0.0
        self.events = []

    def analyze(self, qber):

        self.last_qber = qber

        if qber > self.qber_threshold:

            self.status = "INTRUSION_DETECTED"

            self.events.append({
                "type": "QUANTUM_INTRUSION",
                "qber": qber
            })

        else:

            self.status = "NORMAL"

        return self.status

    def get_status(self):

        return {
            "status": self.status,
            "qber": self.last_qber,
            "threshold": self.qber_threshold,
            "events": self.events
        }