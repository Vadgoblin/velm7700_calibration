from machine import Pin, I2C
from veml7700 import Veml7700
from time import sleep_ms, sleep


if __name__ == '__main__':
    i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=400_000)
    veml = Veml7700(i2c)

    measurements = {}
    for it in (25, 50, 100, 200, 400, 800):
        veml.set_it(it)
        for gain in (0.125, 0.25, 1, 2):
            veml.set_gain(gain)
            sleep_ms(it * 2)

            measurement = veml.read_value()
            raw = measurement['raw']
            normalized_raw = raw / (it * gain)
            print(f"IT: {it:3d} ms | Gain: {gain:5.3f} | raw: {raw:8.0f} | raw_norm: {normalized_raw:8.2f}")