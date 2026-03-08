from machine import Pin, I2C, SPI
from veml7700 import Veml7700
from time import sleep_ms, sleep
from save_measurements import save_measurements

import sdcard, os, vfs

# Constants
SPI_BUS = 1
SCK_PIN = 7
MOSI_PIN = 6
MISO_PIN = 5
CS_PIN = 1
SD_MOUNT_PATH = '/sd'

try:
    # Init SPI communication
    spi = SPI(SPI_BUS, sck=Pin(SCK_PIN), mosi=Pin(MOSI_PIN), miso=Pin(MISO_PIN))
    cs = Pin(CS_PIN)
    sd = sdcard.SDCard(spi, cs)
    # Mount microSD card
    vfs.mount(sd, SD_MOUNT_PATH)
    # List files on the microSD card
    print(os.listdir(SD_MOUNT_PATH))

except Exception as e:
    print('An error occurred:', e)


i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=400_000)
veml = Veml7700(i2c)


def measure_and_save():
    measurements = {}
    for it in (25, 50, 100, 200, 400, 800):
        veml.set_it(it)
        for gain in (0.125, 0.25, 1, 2):
            veml.set_gain(gain)
            sleep_ms(it * 2)

            raw = veml.read_value()["raw"]
            measurements[(it, gain)] = raw

    save_measurements(measurements,directory="/sd/measurements")

while True:
    measure_and_save()
