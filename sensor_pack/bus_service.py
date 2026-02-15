from machine import I2C

class I2cAdapter:
    def __init__(self, i2c: I2C):
        self._i2c = i2c

    def write_register(self, device_addr: int, reg_addr: int, value: int,
                       bytes_count: int, byte_order: str):
        buf = value.to_bytes(bytes_count, byte_order)
        return self._i2c.writeto_mem(device_addr, reg_addr, buf)

    def read_register(self, device_addr: int, reg_addr: int, bytes_count: int) -> bytes:
        return self._i2c.readfrom_mem(device_addr, reg_addr, bytes_count)

    def read(self, device_addr, n_bytes: int) -> bytes:
        return self._i2c.readfrom(device_addr, n_bytes)

    def write(self, device_addr, buf: bytes):
        return self._i2c.writeto(device_addr, buf)