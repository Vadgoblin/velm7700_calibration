import micropython
import ustruct
from machine import I2C
import math


@micropython.native
def _check_value(value: int, valid_range, error_msg: str) -> int:
    if value not in valid_range:
        raise ValueError(error_msg)
    return value


def _unpack(fmt_char: str, source: bytes) -> tuple:
    """распаковка массива, считанного из датчика.
    fmt_char: c, b, B, h, H, i, I, l, L, q, Q. pls see: https://docs.python.org/3/library/struct.html"""
    if len(fmt_char) != 1:
        raise ValueError(f"Invalid length fmt_char parameter: {len(fmt_char)}")
    return ustruct.unpack('<' + fmt_char, source)


class Veml7700:
    """Class for work with ambient Light Sensor VEML7700.
    Please read: https://www.vishay.com/docs/84286/veml7700.pdf"""

    GAIN = (0.125, 0.25, 1, 2)
    INTEGRATION_TIME = (25, 50, 100, 200, 400, 800)
    _IT = 12, 8, 0, 1, 2, 3  # integration time const


    @staticmethod
    def get_max_possible_illumination(gain: int, it: int) -> float:
        raw_it = math.log2(it / 25)
        _g_base = 0.125
        _max_ill = 120796
        _k = gain / _g_base
        return (_max_ill / 2 ** raw_it) / _k

    def __init__(self, i2c: I2C, address: int = 0x10):
        self._i2c = i2c
        self.address = address
        self._gain = 1
        self._it = 200

    def set_gain(self, new_gain):
        if new_gain not in self.GAIN:
            raise Exception("Invalid gain value")
        self._gain = new_gain
        self._update_als()

    def get_gain(self):
        return self._gain

    def set_it(self, new_it):
        if new_it not in self.INTEGRATION_TIME:
            raise Exception("Invalid it value")
        self._it = new_it
        self._update_als()

    def get_it(self):
        return self._it

    def _update_als(self):
        gain_mapper = {1:0, 2:1, 0.125:2, 0.25: 3}
        als_gain = gain_mapper[self._gain]

        als_it = 0
        als_pers = 0
        als_int_en = False
        als_shutdown = False
        self._set_config_als(als_gain, als_it, als_pers, als_int_en, als_shutdown)

    def write_register(self, reg_addr: int, value: int, bytes_count: int) -> None:
        buf = value.to_bytes(bytes_count, "little")
        self._i2c.writeto_mem(self.address, reg_addr, buf)

    def read_register(self, reg_addr: int, bytes_count: int) -> bytes:
        return self._i2c.readfrom_mem(self.address, reg_addr, bytes_count)

    def _set_config_als(self, gain: int, integration_time: int, persistence: int = 1,
                        interrupt_enable: bool = False, shutdown: bool = False):
        """Setting Ambient Light Sensor (ALS) parameters.
        gain = 0..3; 0-gain=1, 1-gain=2, 2-gain=0.125(1/8), 3-gain=0.25(1/4).
        integration_time = 0..5; 0-25 ms; 1-50 ms; 2-100 ms, 3-200 ms, 4-400 ms, 5-800 ms
        persistence protect number = 0..3; 0-1, 1-2, 2-4, 3-8
        """
        _cfg = 0
        _bts = self.read_register(0x00, 2)
        _cfg = _unpack("H", _bts)[0]
        self.write_register(0x00, _cfg | 0x01, 2)

        _cfg = 0
        gain = _check_value(gain, range(4), f"Invalid als gain value: {gain}")
        _tmp = _check_value(integration_time, range(6), f"Invalid als integration_time: {integration_time}")

        it = self._IT[_tmp]

        pers = _check_value(persistence, range(4), f"Invalid als persistence protect number: {persistence}")
        ie = 0
        if interrupt_enable:
            ie = 1
        sd = 0
        if shutdown:
            sd = 1
        _cfg |= sd
        _cfg |= ie << 1
        _cfg |= pers << 4
        _cfg |= it << 6
        _cfg |= gain << 11

        self.write_register(0x00, _cfg, 2)

    def read_value(self):
        raw_value = self._get_raw_value()
        illumination = self._raw_to_illumination(raw_value)
        white_channel = self._get_white_channel()

        return {"raw":raw_value, "illumination":illumination, "white_channel":white_channel}

    def _get_raw_value(self):
        reg_val = self.read_register(0x04, 2)
        raw_lux = _unpack("H", reg_val)[0]
        return raw_lux

    def _get_white_channel(self):
        """Return white channel output data"""
        reg_val = self.read_register(0x05, 2)
        return _unpack("H", reg_val)[0]

    def _raw_to_illumination(self, raw_value) -> float:
        return raw_value * self._get_resolution()

    def _get_resolution(self) -> float:
        raw_it = math.log2(self._it/25)
        _g_base = 0.125
        _max_res = 1.8432
        _k = self._gain / _g_base
        return (_max_res / 2 ** raw_it) / _k

    def __iter__(self):
        return self

    def __next__(self):
        return self.read_value()
