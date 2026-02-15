from machine import I2C, Pin
from veml7700 import Veml7700
from sensor_pack.bus_service import I2cAdapter
import time

if __name__ == '__main__':
    i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400_000)
    adaptor = I2cAdapter(i2c)
    sol = Veml7700(adaptor)

    # _g = 1, 2, 0.125, 0.25
    # 25 * 2 ** raw_it
    sol.set_config_als(gain=0, integration_time=1, persistence=1, interrupt_enable=False, shutdown=False)
    sol.set_power_save_mode(enable_psm=False, psm=0)
    
    delay = old_lux = curr_max = 1
    mpi = Veml7700.get_max_possible_illumination(sol.gain[0], sol.integration_time[0])

    for lux in sol:
        wh = sol.get_white_channel()
        delay = sol.get_conversion_cycle_time()
        print(f"Illum. [lux]: {lux}\traw: {sol.last_raw}\twhite ch.: {wh}\tdelay: {delay} [ms]")

        if lux > 0.95 * mpi:
            print("Too bright, change settings!")
        time.sleep_ms(delay)