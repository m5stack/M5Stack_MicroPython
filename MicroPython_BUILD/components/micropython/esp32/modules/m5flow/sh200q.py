import i2c_bus
import utime as time
import ustruct
from micropython import const
import math

_ADDR = const(0x6c)
_ACC_CONFIG = const(0x0e)
_GYRO_CONFIG = const(0x0f)
_GYRO_DLPF = const(0x11)
_FIFO_CONFIG = const(0x12)
_ACC_RANGE =  const(0x16)
_GYRO_RANGE = const(0x2B)
_OUTPUT_ACC_X = const(0x00)
_OUTPUT_GYRO_X = const(0x06)
_OUTPUT_TEMP = const(0x0C)
_REG_SET1 = const(0xBA)
_REG_SET2 = const(0xCA)   #ADC reset
_ADC_RESET = const(0xC2)   #drive reset
_SOFT_RESET = const(0x7F)
_RESET = const(0x75)

ACCEL_FS_SEL_4G = const(0x00)
ACCEL_FS_SEL_8G = const(0x01)
ACCEL_FS_SEL_16G = const(0x10)

_ACCEL_SO_4G = 8192 # 1 / 8192 ie. 0.122 mg / digit
_ACCEL_SO_8G = 4096 # 1 / 4096 ie. 0.244 mg / digit
_ACCEL_SO_16G = 2048 # 1 / 2048 ie. 0.488 mg / digit

#_GYRO_FS_MASK = const(0b00011000)
GYRO_FS_SEL_250DPS = const(0x03)
GYRO_FS_SEL_500DPS = const(0x02)
GYRO_FS_SEL_1000DPS = const(0x01)

_GYRO_SO_250DPS = 131
_GYRO_SO_500DPS = 65.5
_GYRO_SO_1000DPS = 32.8

SF_G = 1
SF_M_S2 = 9.80665 # 1 g = 9.80665 m/s2 ie. standard gravity
SF_DEG_S = 1
SF_RAD_S = 57.295779513082 # 1 rad/s is 57.295779578552 deg/s

class Sh200q:
    def __init__(self, port=None, accel_fs=ACCEL_FS_SEL_4G, gyro_fs=GYRO_FS_SEL_500DPS):
        if not port:
            port = i2c_bus.M_BUS
        self.i2c = i2c_bus.get(port)
        self._regInit(accel_fs, gyro_fs)

        self.preInterval = time.ticks_us() 
        self.accCoef = 0.02
        self.gyroCoef = 0.98
        self.angleGyroX = 0
        self.angleGyroY = 0
        self.angleGyroZ = 0
        self.angleX = 0
        self.angleZ = 0
        self.angleY = 0
        self.gyroXoffset = 0
        self.gyroYoffset = 0
        self.gyroZoffset = 0

    @property
    def acceleration(self):
        so = self._accel_so
        data = self._regThreeShort(0x00)
        return tuple([round(value / so, 3) for value in data])

    @property
    def gyro(self):
        so = self._gyro_so
        data = self._regThreeShort(0x06)
        return tuple([round(value / so, 3) for value in data])
    
    @property
    def ypr(self):
        accX, accY, accZ = self.acceleration

        angleAccX = math.atan2(accY, accZ + abs(accX)) * SF_RAD_S
        angleAccY = math.atan2(accX, accZ + abs(accY)) * (-SF_RAD_S);

        gyroX, gyroY, gyroZ = self.gyro
        gyroX -= self.gyroXoffset
        gyroY -= self.gyroYoffset
        gyroZ -= self.gyroZoffset

        interval = (time.ticks_us() - self.preInterval) / 1000000
        self.preInterval = time.ticks_us()

        self.angleGyroX += gyroX * interval
        self.angleGyroY += gyroY * interval
        self.angleGyroZ += gyroZ * interval

        self.angleX = (self.gyroCoef * (self.angleX + gyroX * interval)) + (self.accCoef * angleAccX);
        self.angleY = (self.gyroCoef * (self.angleY + gyroY * interval)) + (self.accCoef * angleAccY);
        self.angleZ = self.angleGyroZ
        if self.angleZ > 3600 or self.angleZ < -3600:
            angleZ = 0

        return tuple([round(self.angleZ, 3), round(self.angleX, 3), round(self.angleY, 3)])


    def _regChar(self, reg, value=None, buf=bytearray(1)):
        if value is None:
            self.i2c.readfrom_mem_into(_ADDR, reg, buf)
            return buf[0]

        ustruct.pack_into('<b', buf, 0, value)
        return self.i2c.writeto_mem(_ADDR, reg, buf)

    def _regThreeShort(self, reg, buf=bytearray(6)):
        self.i2c.readfrom_mem_into(_ADDR, reg, buf)
        return ustruct.unpack('<hhh', buf)
    
    def _accel_fs(self, value):
        self._regChar(_ACC_RANGE, value)
        if value == ACCEL_FS_SEL_4G:
            return _ACCEL_SO_4G
        elif value == ACCEL_FS_SEL_8G:
            return _ACCEL_SO_8G
        elif value == ACCEL_FS_SEL_16G:
            return _ACCEL_SO_16G
    
    def _gyro_fs(self, value):
        self._regChar(_GYRO_RANGE, value)
        if value == GYRO_FS_SEL_250DPS:
            return _GYRO_SO_250DPS
        elif value == GYRO_FS_SEL_500DPS:
            return _GYRO_SO_500DPS
        elif value == GYRO_FS_SEL_1000DPS:
            return _GYRO_SO_1000DPS
            
    def _regInit(self, accel_fs, gyro_fs):
        self.adcRest()
        data = self._regChar(0xd8)
        self._regChar(0xd8, data | 0x80)
        time.sleep_ms(1)
        self._regChar(0xd8, data & 0x7f)
        self._regChar(0x78, 0x61)
        time.sleep_ms(1)
        self._regChar(0x78, 0x00)

        self._accel_so = self._accel_fs(accel_fs)
        self._gyro_so = self._gyro_fs(gyro_fs)

        #0x81 1024hz 0x89 512hz 0x91 256hz
        self._regChar(_ACC_CONFIG, 0x91)
        #0x11 1000hz 0x13 500hz 0x15 250hz
        self._regChar(_GYRO_CONFIG, 0x13)
        #0x00 250hz 0x01 200hz 0x02 100hz 0x03 50hz 0x04 25hz
        self._regChar(_GYRO_DLPF, 0x03)
        #no buffer mode
        self._regChar(_FIFO_CONFIG, 0x00)

        self._regChar(_REG_SET1, 0xc0)
        data = self._regChar(_REG_SET2)
        self._regChar(_REG_SET2, data | 0x10)
        time.sleep_ms(1)
        self._regChar(_REG_SET2, data & 0xef)
        time.sleep_ms(10)

    def adcRest(self):
        data = self._regChar(_ADC_RESET)
        self._regChar(_ADC_RESET, data | 0x04)
        time.sleep_ms(1)
        self._regChar(_ADC_RESET, data & 0xfb)

    def deinit(self):
        pass