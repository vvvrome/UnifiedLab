import random


class QuantumChannel:

    def __init__(self, noise_probability=0.0):

        self.noise_probability = noise_probability

    def apply_noise(self, bit):

        if random.random() < self.noise_probability:

            return 1 - bit

        return bit