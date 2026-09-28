from datetime import datetime
from collections import deque

from .qkd import QKDSession
from .intrusion_detector import QuantumIntrusionDetector


class QKDManager:

    def __init__(
        self,
        key_length=256,
        qber_threshold=0.11,
        max_history=100,
        alert_manager=None
    ):

        self.key_length = key_length
        self.qber_threshold = qber_threshold

        self.alert_manager = alert_manager

        self.detector = QuantumIntrusionDetector(
            qber_threshold=qber_threshold
        )

        self.current_key = None

        self.status = "NOT_INITIALIZED"

        self.last_qber = 0.0

        self.last_session = None

        self.session_count = 0

        self.successful_sessions = 0

        self.compromised_sessions = 0

        self.history = deque(
            maxlen=max_history
        )

    # ==================================================
    # CONFIGURAR ALERTAS
    # ==================================================

    def set_alert_manager(self, alert_manager):

        self.alert_manager = alert_manager

    # ==================================================
    # INICIAR SESIÓN QKD
    # ==================================================

    def start_session(self, eve=False):

        self.status = "RUNNING"

        self.session_count += 1

        session = QKDSession(
            key_length=self.key_length
        )

        result = session.run(
            eve=eve,
            qber_threshold=self.qber_threshold
        )

        self.last_session = result

        self.last_qber = result["qber"]

        # ==================================================
        # ANALIZAR QBER
        # ==================================================

        security_status = self.detector.analyze(
            self.last_qber
        )

        # ==================================================
        # CANAL SEGURO
        # ==================================================

        if security_status == "NORMAL":

            self.status = "SECURE"

            self.current_key = session.key

            self.successful_sessions += 1

        # ==================================================
        # INTRUSIÓN DETECTADA
        # ==================================================

        else:

            self.status = "COMPROMISED"

            self.current_key = None

            self.compromised_sessions += 1

            # ==============================================
            # ALERTA DE PLANTA
            # ==============================================

            if self.alert_manager is not None:

                self.alert_manager.add_alert(
                    severity="CRITICAL",
                    message=(
                        "Quantum communication channel "
                        "compromised. Possible interception "
                        "detected."
                    ),
                    device="QKD-01",
                    parameter="QBER",
                    value=self.last_qber * 100
                )

        # ==================================================
        # HISTORIAL
        # ==================================================

        self.history.append({

            "timestamp":
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),

            "session":
                self.session_count,

            "status":
                self.status,

            "qber":
                self.last_qber,

            "key_length":
                len(self.current_key)
                if self.current_key
                else 0,

            "eve_detected":
                self.status == "COMPROMISED"
        })

        return self.get_status()

    # ==================================================
    # INVALIDAR CLAVE
    # ==================================================

    def invalidate_key(self):

        self.current_key = None

        if self.status == "SECURE":

            self.status = "WARNING"

    # ==================================================
    # COMPROBAR CLAVE
    # ==================================================

    def has_valid_key(self):

        return (
            self.current_key is not None
            and self.status == "SECURE"
        )

    # ==================================================
    # ESTADO
    # ==================================================

    def get_status(self):

        return {

            "status":
                self.status,

            "qber":
                round(
                    self.last_qber,
                    4
                ),

            "qber_percent":
                round(
                    self.last_qber * 100,
                    2
                ),

            "qber_threshold":
                self.qber_threshold,

            "key_length":
                len(self.current_key)
                if self.current_key
                else 0,

            "session_count":
                self.session_count,

            "successful_sessions":
                self.successful_sessions,

            "compromised_sessions":
                self.compromised_sessions,

            "eve_detected":
                self.status == "COMPROMISED"
        }

    # ==================================================
    # HISTORIAL
    # ==================================================

    def get_history(self):

        return list(
            self.history
        )

    # ==================================================
    # RESET
    # ==================================================

    def reset(self):

        self.current_key = None

        self.status = "NOT_INITIALIZED"

        self.last_qber = 0.0

        self.last_session = None

        self.session_count = 0

        self.successful_sessions = 0

        self.compromised_sessions = 0

        self.history.clear()

        self.detector.status = "NORMAL"

        self.detector.last_qber = 0.0

        self.detector.events.clear()