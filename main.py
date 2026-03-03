from machine import I2C, Pin
from veml7700 import Veml7700
import time

class TCA9548A:
    def __init__(self, i2c, address=0x70):
        self.i2c = i2c
        self.address = address

    def select(self, channel):
        if channel > 7:
            raise Exception("Invalid channel")
        self.i2c.writeto(self.address, bytes([1 << channel]))


if __name__ == '__main__':
    i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=400_000)
    multiplexer = TCA9548A(i2c)
    multiplexer.select(0)
    # print(i2c.scan())



    sol = Veml7700(i2c)
    sol.set_gain(0.25)
    sol.set_it(400)

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