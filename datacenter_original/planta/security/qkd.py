import random


class QKDSession:
    """
    Simulación simplificada del protocolo BB84.

    Alice:
        Genera bits y bases.

    Canal:
        Transmite los qubits.

    Bob:
        Genera bases y realiza las mediciones.

    Después:
        Alice y Bob comparan públicamente sus bases
        y conservan únicamente los bits compatibles.
    """

    BASES = ["+", "x"]

    def __init__(self, key_length=128):
        self.key_length = key_length

        self.alice_bits = []
        self.alice_bases = []

        self.bob_bases = []
        self.bob_bits = []

        self.sifted_key_alice = []
        self.sifted_key_bob = []

        self.qber = 0.0
        self.key = ""

        self.status = "NOT_STARTED"

    def generate_alice_data(self):
        """Alice genera bits y bases aleatorias."""

        self.alice_bits = [
            random.randint(0, 1)
            for _ in range(self.key_length)
        ]

        self.alice_bases = [
            random.choice(self.BASES)
            for _ in range(self.key_length)
        ]

    def generate_bob_bases(self):
        """Bob genera bases aleatorias."""

        self.bob_bases = [
            random.choice(self.BASES)
            for _ in range(self.key_length)
        ]

    def transmit(self, eve=False):
        """
        Simula la transmisión de los qubits.

        Si Eve está activa utiliza un ataque
        intercept-resend simplificado.
        """

        self.bob_bits = []

        for i in range(self.key_length):

            alice_bit = self.alice_bits[i]
            alice_basis = self.alice_bases[i]
            bob_basis = self.bob_bases[i]

            # Sin Eve
            if not eve:

                if alice_basis == bob_basis:
                    measured_bit = alice_bit
                else:
                    measured_bit = random.randint(0, 1)

                self.bob_bits.append(measured_bit)

            # Eve intercepta y vuelve a transmitir
            else:

                eve_basis = random.choice(self.BASES)

                if eve_basis == alice_basis:
                    eve_bit = alice_bit
                else:
                    eve_bit = random.randint(0, 1)

                if bob_basis == eve_basis:
                    measured_bit = eve_bit
                else:
                    measured_bit = random.randint(0, 1)

                self.bob_bits.append(measured_bit)

    def sift(self):
        """
        Alice y Bob comparan sus bases.

        Conservan únicamente las posiciones
        donde utilizaron la misma base.
        """

        self.sifted_key_alice = []
        self.sifted_key_bob = []

        for i in range(self.key_length):

            if self.alice_bases[i] == self.bob_bases[i]:

                self.sifted_key_alice.append(
                    self.alice_bits[i]
                )

                self.sifted_key_bob.append(
                    self.bob_bits[i]
                )

    def calculate_qber(self):
        """Calcula el Quantum Bit Error Rate."""

        if not self.sifted_key_alice:
            self.qber = 1.0
            return self.qber

        errors = 0

        for alice, bob in zip(
            self.sifted_key_alice,
            self.sifted_key_bob
        ):
            if alice != bob:
                errors += 1

        self.qber = errors / len(self.sifted_key_alice)

        return self.qber

    def generate_key(self, qber_threshold=0.11):
        """
        Genera la clave únicamente si el QBER
        está por debajo del umbral.
        """

        if self.qber > qber_threshold:

            self.key = ""
            self.status = "INTRUSION_DETECTED"

            return False

        self.key = "".join(
            str(bit)
            for bit in self.sifted_key_alice
        )

        self.status = "KEY_ESTABLISHED"

        return True

    def run(self, eve=False, qber_threshold=0.11):
        """Ejecuta una sesión BB84 completa."""

        self.status = "RUNNING"

        self.generate_alice_data()
        self.generate_bob_bases()

        self.transmit(eve=eve)

        self.sift()

        self.calculate_qber()

        self.generate_key(
            qber_threshold=qber_threshold
        )

        return self.get_status()

    def get_status(self):

        return {
            "status": self.status,
            "qber": round(self.qber, 4),
            "key_length": len(self.key),
            "raw_bits": self.key_length,
            "sifted_bits": len(self.sifted_key_alice),
            "eve_detected": self.status == "INTRUSION_DETECTED"
        }