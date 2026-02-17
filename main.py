from machine import I2C, Pin
from veml7700 import Veml7700
import time

if __name__ == '__main__':
    i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400_000)
    sol = Veml7700(i2c)
    sol.set_gain(0.125)
    sol.set_it(25)

    # _g = 1, 2, 0.125, 0.25
    # 25 * 2 ** raw_it
    #sol.set_config_als(gain=1, integration_time=5, persistence=1, interrupt_enable=False, shutdown=False)
    # sol.set_power_save_mode(enable_psm=False, psm=0)
    
    delay = old_lux = curr_max = 1
    # mpi = Veml7700.get_max_possible_illumination(sol.get_gain(), sol.get_it())

    for lux in sol:
        wh = sol.get_white_channel()
        delay = sol.get_it()
        print(f"Illum. [lux]: {lux}\traw: \twhite ch.: {wh}\tdelay: {delay} [ms]")

        # if lux > 0.95 * mpi:
        #     print("Too bright, change settings!")
        time.sleep_ms(delay)