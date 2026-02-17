from machine import I2C, Pin
from veml7700 import Veml7700
import time

if __name__ == '__main__':
    i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400_000)
    sol = Veml7700(i2c)
    sol.set_gain(2)
    sol.set_it(800)

    mpi =sol.get_max_possible_illumination()

    for measurement in sol:
        delay = sol.get_it() + 100

        raw = measurement["raw"]
        lux = measurement["illumination"]
        white = measurement["white_channel"]

        print(f"Illum. [lux]: {lux}\traw: {raw}\twhite ch.: {white}\tdelay: {delay} [ms]")

        if lux > 0.95 * mpi:
            print("Too bright, change settings!")
        time.sleep_ms(delay)