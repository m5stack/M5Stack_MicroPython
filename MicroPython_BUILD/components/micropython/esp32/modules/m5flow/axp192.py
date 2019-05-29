import machine
import ustruct
import i2c_bus

class Axp192:
    def __init__(self):
        self.addr = 0x34
        self.i2c = i2c_bus.get(i2c_bus.M_BUS)
    
    def powerAll(self):
        regchar = self._regChar
        regchar(0x10, 0xff)
        regchar(0x28, 0xff)
        regchar(0x82, 0xff)
        regchar(0x33, 0xc0)
        regchar(0x33, 0xc3)
        regchar(0xb8, 0x80)
        regchar(0x12, 0x4d)
        regchar(0x36, 0x5c)
        regchar(0x90, 0x02)

    def _regChar(self, reg, value=None, buf=bytearray(1)):
        if value is None:
            self.i2c.readfrom_mem_into(self.addr, reg, buf)
            return buf[0]

        ustruct.pack_into('<b', buf, 0, value)
        return self.i2c.writeto_mem(self.addr, reg, buf)

    def deinit(self):
        pass