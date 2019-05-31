import ustruct
import i2c_bus


class RTC:
    def __init__(self):
        self.addr = 0x51
        self.i2c = i2c_bus.get(i2c_bus.M_BUS)

    def getTime(self):
        buf = self._regChar(0x02, buf=bytearray(3))

        seconds = self.bcd2ToByte(buf[0] & 0x7f)
        minutes = self.bcd2ToByte(buf[1] & 0x7f)
        hours = self.bcd2ToByte(buf[2] & 0x3f)

        return hours, minutes, seconds

    def setTime(self, hours, minutes, seconds):
        seconds = self.byteToBcd2(seconds)
        minutes = self.byteToBcd2(minutes)
        hours = self.byteToBcd2(hours)

        self._regChar(0x02, (seconds, minutes, hours), buf=bytearray(3))

    def getDate(self):
        buf = self._regChar(0x05, buf=bytearray(4))

        date = self.bcd2ToByte(buf[0] & 0x3f)
        week_day = self.bcd2ToByte(buf[1] & 0x07)
        month = self.bcd2ToByte(buf[2] & 0x1f)

        if buf[2] & 0x80:
            year = 1900 + self.bcd2ToByte(buf[3] & 0xff)
        else:
            year = 2000 + self.bcd2ToByte(buf[3] & 0xff)

        return year, month, date, week_day

    def setDate(self, year, month, date, week_day):
        date = self.byteToBcd2(date)
        week_day = self.byteToBcd2(week_day)

        if year < 2000:
            month = self.byteToBcd2(month | 0x80)
        else:
            month = self.byteToBcd2(month | 0x00)

        year = self.byteToBcd2(year % 100)

        self._regChar(0x05, (date, week_day, month, year), buf=bytearray(4))

    def _regChar(self, reg, value=None, buf=bytearray(1)):
        if value is None:
            self.i2c.readfrom_mem_into(self.addr, reg, buf)
            if len(buf) == 1:
                return buf[0]
            else:
                return buf

        if type(value) is int:
            ustruct.pack_into('<b', buf, 0, value)
        else:
            ustruct.pack_into('<%db' % len(value), buf, 0, *value)

        return self.i2c.writeto_mem(self.addr, reg, buf)

    def bcd2ToByte(self, value):
        tmp = ((value & 0xF0) >> 0x4) * 10
        return tmp + (value & 0x0F)

    def byteToBcd2(self, value):
        bcdhigh = 0

        while value >= 10:
            bcdhigh += 1
            value -= 10

        return (bcdhigh << 4) | value
