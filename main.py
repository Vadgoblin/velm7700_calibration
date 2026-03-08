from machine import Pin
from multi_veml7700 import MultiVeml7700
from time import sleep_ms

if __name__ == '__main__':
    multi_veml = MultiVeml7700(0, scl=Pin(9), sda=Pin(8), freq=400_000, count=3)

    multi_veml.set_gain(0.125)
    multi_veml.set_it(100)

    while True:
        measurement = multi_veml.read_values()
        print(measurement)
        sleep_ms(110)
