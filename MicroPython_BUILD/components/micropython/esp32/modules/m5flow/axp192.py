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

    def screenBreath(self, brightness):
        self._regChar(0x28, ((brightness & 0x0f) << 4))

    def enableCoulombCounter(self):
        self._regChar(0xb8, 0x80)

    def disableCoulombCounter(self):
        self._regChar(0xb8, 0x00)

    def stopCoulombCounter(self):
        self._regChar(0xb8, 0xc0)

    def clearCoulombCounter(self):
        self._regChar(0xb8, 0xa0)

    def getCoulombChargeData(self):
        buf = self._regChar(0xb0)
        buf1 = self._regChar(0xb1)
        buf2 = self._regChar(0xb2)
        buf3 = self._regChar(0xb3)

        return (buf << 24) + (buf1 << 16) + (buf2 << 8) + buf3

    def getCoulombDischargeData(self):
        buf = self._regChar(0xb4)
        buf1 = self._regChar(0xb5)
        buf2 = self._regChar(0xb6)
        buf3 = self._regChar(0xb7)

        return (buf << 24) + (buf1 << 16) + (buf2 << 8) + buf3

    def getCoulombData(self):
        coin = self.getCoulombChargeData()
        coout = self.getCoulombDischargeData()

        return 65536 * 0.5 * (coin - coout) / 3600.0 / 25.0

    def getVbatData(self):
        buf = self._regChar(0x78)
        buf1 = self._regChar(0x79)

        return (buf << 4) + buf1

    def getVinData(self):
        buf = self._regChar(0x56)
        buf1 = self._regChar(0x57)

        return (buf << 4) + buf1

    def getIinData(self):
        buf = self._regChar(0x58)
        buf1 = self._regChar(0x59)

        return (buf << 4) + buf1

    def getIChargeData(self):
        buf = self._regChar(0x7a)
        buf1 = self._regChar(0x7b)

        return (buf << 5) + buf1

    def getIDischargeData(self):
        buf = self._regChar(0x7c)
        buf1 = self._regChar(0x7d)

        return (buf << 5) + buf1

    def getTempData(self):
        buf = self._regChar(0x5e)
        buf1 = self._regChar(0x5f)

        return (buf << 4) + buf1

    def getPowerBatData(self):
        buf = self._regChar(0x70)
        buf1 = self._regChar(0x71)
        buf2 = self._regChar(0x72)

        return (buf << 16) + (buf1 << 8) + buf2

    def getVapsData(self):
        buf = self._regChar(0x7e)
        buf1 = self._regChar(0x7f)

        return (buf << 4) + buf1

    def setSleep(self):
        buf = self._regChar(0x31)
        buf = (1 << 3) | buf

        self._regChar(0x31, buf)
        self._regChar(0x12, 0x41)

    def getWarningLevel(self):
        buf = self._regChar(0x47)

        return buf & 0x01

    def _regChar(self, reg, value=None, buf=bytearray(1)):
        if value is None:
            self.i2c.readfrom_mem_into(self.addr, reg, buf)
            return buf[0]

        ustruct.pack_into('<b', buf, 0, value)
        return self.i2c.writeto_mem(self.addr, reg, buf)

    def deinit(self):
        pass