from time import sleep_ms, sleep
import random
from machine import I2C, Pin, PWM
from veml7700 import Veml7700




class SmartLightMeter:
    def __init__(self, veml_instance, multipliers):
        self.veml = veml_instance
        self.multipliers = multipliers
        self.gears = [(400, 2.0), (100, 1.0), (50, 0.25), (25, 0.125)]

        self.UPPER_THRESH = 10000
        self.LOWER_THRESH = 1000  # Prevents infinite gear-shifting loops

        self.current_gear = 0

    def _read_dithered(self, it, gain):
        self.veml.set_it(it)
        self.veml.set_gain(gain)
        raws = []
        for _ in range(10):
            self.veml.power_off()
            sleep_ms(random.randint(1, 7))
            self.veml.power_on()
            sleep_ms(it * 2)
            raws.append(self.veml.read_value()["raw"])
        return sum(raws) / len(raws)

    def get_ambient_light(self):
        """
        Takes a random ambient light reading, automatically hunting
        for the correct gear using hysteresis memory.
        """
        while True:
            it, gain = self.gears[self.current_gear]

            # Take a quick, single peek to check the gear
            self.veml.set_it(it)
            self.veml.set_gain(gain)
            sleep_ms(it * 2)
            quick_raw = self.veml.read_value()["raw"]

            # Shift UP if too bright
            if quick_raw > self.UPPER_THRESH and self.current_gear < len(self.gears) - 1:
                self.current_gear += 1
                continue

            # Shift DOWN if too dim
            elif quick_raw < self.LOWER_THRESH and self.current_gear > 0:
                self.current_gear -= 1
                continue

            # Goldilocks Zone! Gear is perfect. Break the loop.
            break

            # Now that we are in the perfect gear, take the high-accuracy dithered reading
        perfect_raw = self._read_dithered(*self.gears[self.current_gear])

        # Apply the specific calibration for this sensor
        true_light = perfect_raw * self.multipliers[self.current_gear]
        return true_light

# --- HARDWARE SETUP ---
i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=400_000)
veml = Veml7700(i2c)
pwm = PWM(Pin(0))
pwm.freq(500)

# 2. Feed it the array you got from the Calibration Script
SENSOR_MULTIPLIERS = [1.0, 7.99144368, 13.066542, 51.876304]


meter = SmartLightMeter(veml, SENSOR_MULTIPLIERS)





steps = 100
gamma = 2.2

measurements = {}

for i in range(steps + 1):
    x = 1 - (i / steps)
    duty = int((x ** gamma) * 65535)
    pwm.duty_u16(duty)

    current_light = meter.get_ambient_light()
    print(i, current_light)

    measurements[i] = current_light



print()
print()
print()
print(measurements)




# 3. Read perfect light anywhere, anytime
#
# print(f"True Room Brightness: {current_light}")


# GEARS = [(400, 2.0), (100, 1.0), (50, 0.25), (25, 0.125)]
# SHIFT_THRESHOLD = 10000
#
#
# def read_dithered(it, gain, samples=20):
#     veml.set_it(it)
#     veml.set_gain(gain)
#     raws = []
#     for _ in range(samples):
#         veml.power_off()
#         sleep_ms(random.randint(1, 7))
#         veml.power_on()
#         sleep_ms(it * 2)
#         raws.append(veml.read_value()["raw"])
#     return sum(raws) / len(raws)
#
#
# def run_binary_calibration():
#     STEPS = 13
#
#     print("Starting Lightning-Fast Binary Calibration...")
#     multipliers = [1.0]
#
#     for current_gear in range(len(GEARS) - 1):
#         print(f"\nHunting for Gear {current_gear} -> {current_gear + 1} boundary...")
#
#         low_pwm = 0
#         high_pwm = 65535
#         best_pwm = 0
#         it, gain = GEARS[current_gear]
#
#         for step in range(STEPS):
#             mid_pwm = (low_pwm + high_pwm) // 2
#             pwm.duty_u16(mid_pwm)
#
#             # CRITICAL: Wait for the sensor to flush the old light!
#             # We wait 3x the integration time to ensure a perfectly clean new frame.
#             sleep_ms(it * 3)
#
#             # Read the current light
#             raw = read_dithered(it, gain, samples=10)
#             print(f"  Step {step + 1}/{STEPS} | PWM: {mid_pwm} | Raw: {raw:.1f}")
#
#             # Binary Search Logic
#             if raw < SHIFT_THRESHOLD:
#                 low_pwm = mid_pwm + 1  # Too dim, search the upper half
#             else:
#                 high_pwm = mid_pwm - 1  # Too bright, search the lower half
#                 best_pwm = mid_pwm  # Save this as our closest overshoot
#
#         # --- CALCULATION ---
#         # The binary search has narrowed in on the exact PWM where the light crosses 10,000.
#         print(f"Target locked at PWM {best_pwm}. Calculating ratio...")
#
#         # 1. Set the exact boundary PWM
#         pwm.duty_u16(best_pwm)
#         sleep_ms(it * 3)
#
#         # 2. Get the highly accurate, 50-sample dithered reading in the CURRENT gear
#         raw_before = read_dithered(*GEARS[current_gear], samples=50)
#         true_light = raw_before * multipliers[current_gear]
#
#         # 3. Shift to the NEXT gear, wait for it to settle, and read the SAME physical light
#         next_it, next_gain = GEARS[current_gear + 1]
#         sleep_ms(next_it * 3)
#         raw_after = read_dithered(next_it, next_gain, samples=50)
#
#         # 4. Calculate the  multiplier
#         new_multiplier = true_light / raw_after
#         multipliers.append(new_multiplier)
#
#         print(f"Gear {current_gear + 1} Multiplier Locked: {new_multiplier:.4f}")
#
#     pwm.duty_u16(0)
#     print("\n--- BINARY CALIBRATION COMPLETE ---")
#     print(f"SENSOR_MULTIPLIERS = {multipliers}")
#
#
# run_binary_calibration()

# SENSOR_MULTIPLIERS = [1.0, 7.990809, 13.108759, 52.43662]
# SENSOR_MULTIPLIERS = [1.0, 7.991282, 13.067235, 52.66941]
# SENSOR_MULTIPLIERS = [1.0, 7.99144368, 13.066542, 51.876304]