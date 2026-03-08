from machine import I2C, Pin
from tca9548a import TCA9548A
from veml7700 import Veml7700


class MultiVeml7700:
    def __init__(self, id, scl, sda, freq: int = 400_000, count=1):
        i2c = I2C(id, scl=Pin(scl), sda=Pin(sda), freq=freq)
        self._multiplexer = TCA9548A(i2c)
        self._sensors: list[Veml7700] = []

        for i in range(count):
            self._multiplexer.select(i)
            i2c = I2C(id, scl=Pin(scl), sda=Pin(sda), freq=freq)
            sol = Veml7700(i2c)
            self._sensors.append(sol)

    def set_gain(self, new_gain):
        for i in range(len(self._sensors)):
            self._multiplexer.select(i)
            self._sensors[i].set_gain(new_gain)

    def set_it(self, new_it):
        for i in range(len(self._sensors)):
            self._multiplexer.select(i)
            self._sensors[i].set_it(new_it)

    def read_values(self):
        values = {}
        for i in range(len(self._sensors)):
            sensor = self._sensors[i]
            values[i] = sensor.read_value()

        return values
