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
SHIFT_THRESHOLD = 10000


def read_dithered(it, gain):
    veml.set_it(it)
    veml.set_gain(gain)
    raws = []
    for _ in range(10):
        veml.power_off()
        sleep_ms(random.randint(1, 7))
        veml.power_on()
        sleep_ms(it * 2)  # Give it time to integrate
        raws.append(veml.read_value()["raw"])
    return sum(raws) / len(raws)


def run_calibration():
    print("Starting Automated Boundary Calibration...")
    multipliers = [1.0]
    current_gear = 0
    current_pwm = 0

    # We use a Gamma curve to increment the LED smoothly
    for step in range(1000):  # 1000 very fine steps
        x = step / 1000.0
        current_pwm = int((x ** 2.2) * 65535)
        pwm.duty_u16(current_pwm)

        # Read the light in the current gear
        raw = read_dithered(*GEARS[current_gear])

        # Did we hit the boundary?
        if raw >= SHIFT_THRESHOLD:
            if current_gear < len(GEARS) - 1:
                print(f"Boundary hit at PWM {current_pwm}. Calculating ratio...")

                # We are frozen right at the ~10,000 threshold.
                # Calculate the exact light value using the current gear.
                true_light_before_shift = raw * multipliers[current_gear]

                # Shift to the NEXT gear and take a reading of the exact same light
                next_gear_raw = read_dithered(*GEARS[current_gear + 1])

                # Calculate the exact multiplier needed to bridge the gap
                new_multiplier = true_light_before_shift / next_gear_raw
                multipliers.append(new_multiplier)

                print(f"Gear {current_gear + 1} Multiplier Locked: {new_multiplier:.4f}")
                current_gear += 1
            else:
                break  # We calibrated all gears!

    pwm.duty_u16(0)
    print("\n--- CALIBRATION COMPLETE ---")
    print(f"Save these multipliers for this specific sensor:")
    print(f"SENSOR_MULTIPLIERS = {multipliers}")


run_calibration()

# SENSOR_MULTIPLIERS = [1.0, 7.9904016, 13.178978, 53.42643]