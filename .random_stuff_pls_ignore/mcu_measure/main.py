from machine import Pin, I2C
from veml7700 import Veml7700
from time import sleep_ms, sleep
from save_measurements import save_measurements


i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=400_000)
veml = Veml7700(i2c)

measurements = {}
for it in (25, 50, 100, 200, 400, 800):
    veml.set_it(it)
    for gain in (0.125, 0.25, 1, 2):
        veml.set_gain(gain)
        sleep_ms(it* 2)

        raws = []
        for _ in range(5):
            sleep_ms(it)
            raw = veml.read_value()["raw"]
            raws.append(raw)
        avg = sum(raws) / len(raws)
        measurements[(it, gain)] = avg

save_measurements(measurements)

# turn on built in led to signal that the measurement is finished
pin = Pin(8, mode=Pin.OUT)
pin.value(0)
sleep(60*60)