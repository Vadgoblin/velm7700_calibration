from machine import Pin
from multi_veml7700 import MultiVeml7700
from time import sleep_ms, sleep
from average_sensor_readings import average_sensor_readings

if __name__ == '__main__':
    multi_veml = MultiVeml7700(0, scl=Pin(9), sda=Pin(8), freq=400_000, count=3)

    measurements = {}
    for it in (25, 50, 100, 200, 400, 800):
        multi_veml.set_it(it)
        for gain in (0.125, 0.25, 1, 2):
            multi_veml.set_gain(gain)
            sleep_ms(it * 2)

            measurement_to_avg = []
            for i in range(10):
                measurement = multi_veml.read_values()
                measurement_to_avg.append(measurement)

            measurement_avg = average_sensor_readings(measurement_to_avg)


            measurements[(it,gain)] = measurement_avg

    print(measurements)
    p = Pin(8,mode=Pin.OUT)
    p.value(0)

    sleep(99999)