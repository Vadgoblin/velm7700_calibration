from time import sleep_ms, sleep
from machine import I2C, Pin, PWM
import random

from veml7700 import Veml7700

# Your validated safe gears: (IT, Gain)
GEARS = [
    (400, 2.0),  # Gear 0: Dim light
    (100, 1.0),  # Gear 1: Normal room
    (50, 0.25),  # Gear 2: Bright light
    (25, 0.125)  # Gear 3: Very bight light
]

# # Your empirically calculated multipliers
# GEAR_MULTIPLIERS = [
#     1.0,      # Gear 0
#     8.002,    # Gear 1
#     11.72,    # Gear 2
#     46.83     # Gear 3
# ]

SHIFT_THRESHOLD = 10000


def read_light_dithered(it, gain):
    veml.set_it(it)
    veml.set_gain(gain)

    # --- THE PHASE DITHERING LOOP ---
    raws = []
    for _ in range(10):
        # 1. Halt the sensor's internal clock
        veml.power_off()

        # 2. Wait a random amount of time (e.g., 1 to 7 ms)
        # This completely scrambles the alignment between the shutter and the PWM
        sleep_ms(random.randint(1, 7))

        # 3. Wake the sensor up (Starts a fresh, randomly-aligned integration window)
        veml.power_on()

        # 4. Wait for the shutter to finish
        sleep_ms(it * 3)

        # 5. Read the randomly phased value
        raw = veml.read_value()["raw"]
        raws.append(raw)

    avg_raw = sum(raws) / len(raws)

    return avg_raw


i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=400_000)
veml = Veml7700(i2c)

pwm = PWM(Pin(0))
pwm.freq(500)


steps = 10
gamma = 2.2

gear = 0
gear_multipliers = [1.0]


for i in range(steps + 1):
    gear_shift = False

    #setting pwm duty cycle
    x = i / steps
    duty = int((x ** gamma) * 65535)
    pwm.duty_u16(duty)
    print(f"step: {i}/{steps}\tduty: {duty}\t", end="")

    # reading and processing data from sensor
    raw_value = read_light_dithered(*GEARS[gear])
    multiplier = gear_multipliers[gear]
    adjusted_value = raw_value * multiplier

    if raw_value >= SHIFT_THRESHOLD and gear < len(GEARS) -1:
        previous_gear_adjusted_value = adjusted_value
        gear += 1
        gear_shift = True

        raw_value = read_light_dithered(*GEARS[gear])

        if raw_value >= SHIFT_THRESHOLD:
            raise Exception("Too big brightness change!")

        multiplier = (previous_gear_adjusted_value / raw_value)
        gear_multipliers.append(multiplier)

    print(f"gear:{gear}\traw_value:{raw_value}\tmultiplier:{multiplier}{"\tGear shift!" if gear_shift else ""}")


print("GEAR_MULTIPLIERS = [")

for i in range(len(gear_multipliers)):
    print(f"\t{gear_multipliers[i]}\t# gear {i}")

print("]")

