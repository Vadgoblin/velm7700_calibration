class TCA9548A:
    def __init__(self, i2c, address=0x70):
        self.i2c = i2c
        self.address = address

    def select(self, channel):
        if channel > 7:
            raise Exception("Invalid channel")
        self.i2c.writeto(self.address, bytes([1 << channel]))