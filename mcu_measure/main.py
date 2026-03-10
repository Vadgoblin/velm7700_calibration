import json
from time import sleep_ms, sleep
from machine import I2C, Pin, PWM

from veml7700 import Veml7700

# Your validated safe gears: (IT, Gain)
GEARS = [
    (400, 2.0),   # Gear 0: Dim light
    (100, 1.0),   # Gear 1: Normal room
    (50, 0.25),   # Gear 2: Bright light
    (25, 0.125)   # Gear 3: "Sunglasses" (Sunlight)
]

# Your empirically calculated multipliers
GEAR_MULTIPLIERS = [
    1.0,      # Gear 0
    8.002,    # Gear 1
    11.72,    # Gear 2
    46.83     # Gear 3
]

SHIFT_THRESHOLD = 10000

import random
from time import sleep_ms


def read_true_ambient_light_dithered():
    for gear_idx in range(len(GEARS)):
        it, gain = GEARS[gear_idx]

        veml.set_it(it)
        veml.set_gain(gain)
        sleep_ms(it * 2)

        # Quick peek to see if we need a lower gear
        if veml.read_value()["raw"] > SHIFT_THRESHOLD and gear_idx < len(GEARS) - 1:
            continue


        # --- THE PHASE DITHERING LOOP ---
        raws = []
        for _ in range(10):
            # 1. Halt the sensor's internal clock (Software Power Off)
            veml.power_off()

            # 2. The Magic: Wait a random amount of time (e.g., 1 to 7 ms)
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

        # Apply your custom cumulative multiplier
        true_stitched_light = avg_raw * GEAR_MULTIPLIERS[gear_idx]

        return true_stitched_light


i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=400_000)
veml = Veml7700(i2c)

pwm = PWM(Pin(0))
pwm.freq(500)

for i in range(60,0,-1):
    print(i)
    sleep(1)
print("start")



steps = 100
gamma = 2.2

measurements = {}

for i in range(steps + 1):
    x = i / steps
    duty = int((x ** gamma) * 65535)
    pwm.duty_u16(duty)
    sleep(2)
    print(duty)
    # measure_and_save()
    measurements[i] = read_true_ambient_light_dithered()
    sleep(0.5)

    with open("result.json", "w") as f:
        json.dump(measurements, f)

# turn on built in led to signal that the measurement is finished
pin = Pin(8, mode=Pin.OUT)
pin.value(0)
sleep(60*60)