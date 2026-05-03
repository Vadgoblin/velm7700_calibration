from time import sleep_ms
import random
from machine import I2C, Pin, PWM
from veml7700 import Veml7700

# --- HARDWARE SETUP ---
i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=400_000)
veml = Veml7700(i2c)
pwm = PWM(Pin(0))
pwm.freq(500)

GEARS = [(400, 2.0), (100, 1.0), (50, 0.25), (25, 0.125)]
SHIFT_THRESHOLD = 10000


def read_dithered(it, gain, samples=20):
    veml.set_it(it)
    veml.set_gain(gain)
    raws = []
    for _ in range(samples):
        veml.power_off()
        sleep_ms(random.randint(1, 7))
        veml.power_on()
        sleep_ms(it * 2)
        raws.append(veml.read_value()["raw"])
    return sum(raws) / len(raws)


def run_binary_calibration():
    STEPS = 13

    print("Starting Lightning-Fast Binary Calibration...")
    multipliers = [1.0]

    for current_gear in range(len(GEARS) - 1):
        print(f"\nHunting for Gear {current_gear} -> {current_gear + 1} boundary...")

        low_pwm = 0
        high_pwm = 65535
        best_pwm = 0
        it, gain = GEARS[current_gear]

        for step in range(STEPS):
            mid_pwm = (low_pwm + high_pwm) // 2
            pwm.duty_u16(mid_pwm)

            # CRITICAL: Wait for the sensor to flush the old light!
            # We wait 3x the integration time to ensure a perfectly clean new frame.
            sleep_ms(it * 3)

            # Read the current light
            raw = read_dithered(it, gain, samples=10)
            print(f"  Step {step + 1}/{STEPS} | PWM: {mid_pwm} | Raw: {raw:.1f}")

            # Binary Search Logic
            if raw < SHIFT_THRESHOLD:
                low_pwm = mid_pwm + 1  # Too dim, search the upper half
            else:
                high_pwm = mid_pwm - 1  # Too bright, search the lower half
                best_pwm = mid_pwm  # Save this as our closest overshoot

        # --- CALCULATION ---
        # The binary search has narrowed in on the exact PWM where the light crosses 10,000.
        print(f"Target locked at PWM {best_pwm}. Calculating ratio...")

        # 1. Set the exact boundary PWM
        pwm.duty_u16(best_pwm)
        sleep_ms(it * 3)

        # 2. Get the highly accurate, 50-sample dithered reading in the CURRENT gear
        raw_before = read_dithered(*GEARS[current_gear], samples=50)
        true_light = raw_before * multipliers[current_gear]

        # 3. Shift to the NEXT gear, wait for it to settle, and read the SAME physical light
        next_it, next_gain = GEARS[current_gear + 1]
        sleep_ms(next_it * 3)
        raw_after = read_dithered(next_it, next_gain, samples=50)

        # 4. Calculate the  multiplier
        new_multiplier = true_light / raw_after
        multipliers.append(new_multiplier)

        print(f"Gear {current_gear + 1} Multiplier Locked: {new_multiplier:.4f}")

    pwm.duty_u16(0)
    print("\n--- BINARY CALIBRATION COMPLETE ---")
    print(f"SENSOR_MULTIPLIERS = {multipliers}")


run_binary_calibration()
