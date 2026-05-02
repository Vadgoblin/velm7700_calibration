from time import sleep_ms
import random
from machine import I2C, Pin, PWM
from veml7700 import Veml7700  # Your custom class

# --- HARDWARE SETUP ---
i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=400_000)
veml = Veml7700(i2c)
pwm = PWM(Pin(0))
pwm.freq(500)

GEARS = [(400, 2.0), (100, 1.0), (50, 0.25), (25, 0.125)]


def read_dithered(it, gain):
    veml.set_it(it)
    veml.set_gain(gain)
    raws = []
    for _ in range(50):
        veml.power_off()
        sleep_ms(random.randint(1, 7))
        veml.power_on()
        sleep_ms(it * 2)  # Give it time to integrate
        raws.append(veml.read_value()["raw"])
    return sum(raws) / len(raws)

def read(it, gain):
    veml.set_it(it)
    veml.set_gain(gain)
    sleep_ms(it * 2)

    raws = []
    for _ in range(10):
        raws.append(veml.read_value()["raw"])
    return sum(raws) / len(raws)


# STEPS_TOTAL = 200
# measurements = {}
#
# for step in range(STEPS_TOTAL):
#     print(step)
#
#     x = step / STEPS_TOTAL
#     current_pwm = int((x ** 2.2) * 65535)
#     pwm.duty_u16(current_pwm)
#
#     l = {}
#     for i in range(len(GEARS)):
#         raw = read_dithered(*GEARS[i])
#         l[i] = raw
#
#     measurements[step] = l
#
# print(measurements)


pwm.duty_u16(int(65535 * 0.5))
for _ in range(5):
    for i in range(len(GEARS)):
        raw = read_dithered(*GEARS[i])
        print(i, raw)

    print()