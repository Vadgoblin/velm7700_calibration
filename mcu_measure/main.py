from machine import Pin, I2C, SPI
from veml7700 import Veml7700
from time import sleep_ms, sleep
from save_measurements import save_measurements

import sdcard, os, vfs

ERROR_LED = Pin(21, mode=Pin.OUT)
ERROR_LED.value(0)

# Constants
SPI_BUS = 1
SCK_PIN = 7
MOSI_PIN = 6
MISO_PIN = 5
CS_PIN = 1
SD_MOUNT_PATH = '/sd'


# --- SD Card Setup ---
try:
    spi = SPI(SPI_BUS, sck=Pin(SCK_PIN), mosi=Pin(MOSI_PIN), miso=Pin(MISO_PIN))
    cs = Pin(CS_PIN)
    sd = sdcard.SDCard(spi, cs)
    vfs.mount(sd, SD_MOUNT_PATH)
    print(os.listdir(SD_MOUNT_PATH))

except Exception as e:
    print('SD Card Error:', e)
    # Blink endlessly if the SD card fails (since we can't save anyway)
    while True:
        ERROR_LED.value(1)
        sleep(0.5)
        ERROR_LED.value(0)
        sleep(0.5)


# --- Sensor Setup ---
def init_sensor():
    """Initializes and returns the sensor object so we can easily reboot it on failure."""
    i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=400_000)
    return Veml7700(i2c)


veml = init_sensor()


def measure_and_save():
    measurements = {}
    for it in (25, 50, 100, 200, 400, 800):
        veml.set_it(it)
        for gain in (0.125, 0.25, 1, 2):
            veml.set_gain(gain)
            sleep_ms(it * 2)

            raw = veml.read_value()["raw"]
            measurements[(it, gain)] = raw

    save_measurements(measurements, directory="/sd/measurements")
    print("Measurement saved successfully.")


# --- The Bulletproof Loop ---
while True:
    try:
        measure_and_save()

    except Exception as e:
        print(f"Crash detected! Error: {e}")

        # 1. Blink twice quickly to signal an error
        for _ in range(2):
            ERROR_LED.value(1)
            sleep(0.3)
            ERROR_LED.value(0)
            sleep(0.3)

        # 2. Wait a moment to let the hardware settle
        sleep(1)

        # 3. Reboot the sensor (fixes I2C lockups)
        try:
            print("Attempting to re-initialize sensor...")
            veml = init_sensor()
        except Exception as reinit_error:
            print(f"Failed to reboot sensor: {reinit_error}")