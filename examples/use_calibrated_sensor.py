from time import sleep_ms, sleep
import random
from machine import I2C, Pin, PWM
from veml7700 import Veml7700


class SmartLightMeter:
    def __init__(self, veml_instance, multipliers):
        self.veml = veml_instance
        self.multipliers = multipliers
        self.gears = [(400, 2.0), (100, 1.0), (50, 0.25), (25, 0.125)]

        self.UPPER_THRESH = 10000
        self.LOWER_THRESH = 1000

        self.current_gear = 0

    def _read_dithered(self, it, gain):
        self.veml.set_it(it)
        self.veml.set_gain(gain)
        raws = []
        for _ in range(10):
            self.veml.power_off()
            sleep_ms(random.randint(1, 7))
            self.veml.power_on()
            sleep_ms(it * 2)
            raws.append(self.veml.read_value()["raw"])
        return sum(raws) / len(raws)

    def get_ambient_light(self):
        """
        Takes a random ambient light reading, automatically hunting
        for the correct gear using hysteresis memory.
        """
        while True:
            it, gain = self.gears[self.current_gear]

            # Take a quick, single peek to check the gear
            self.veml.set_it(it)
            self.veml.set_gain(gain)
            sleep_ms(it * 2)
            quick_raw = self.veml.read_value()["raw"]

            # Shift UP if too bright
            if quick_raw > self.UPPER_THRESH and self.current_gear < len(self.gears) - 1:
                self.current_gear += 1
                continue

            # Shift DOWN if too dim
            elif quick_raw < self.LOWER_THRESH and self.current_gear > 0:
                self.current_gear -= 1
                continue

            break

            # Now that we are in the perfect gear, take the dithered reading
        perfect_raw = self._read_dithered(*self.gears[self.current_gear])

        # Apply the specific calibration for this sensor
        true_light = perfect_raw * self.multipliers[self.current_gear]
        return true_light


# --- HARDWARE SETUP ---
i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=400_000)
veml = Veml7700(i2c)

# Sensor calibration
SENSOR_MULTIPLIERS = [1.0, 7.99144368, 13.066542, 51.876304]

meter = SmartLightMeter(veml, SENSOR_MULTIPLIERS)

while True:
    measurement = meter.get_ambient_light()
    print(measurement)
    sleep(1)
