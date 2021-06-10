""" CardKB, Mini I2C Keyboard - read the raw values over I2C

    This is not the recommanded read usage BUT may be useful for debugging

Author(s):
* Meurisse D for MC Hobby sprl

See Github: https://github.com/mchobby/esp8266-upy/tree/master/cardkb
"""

from machine import I2C
from cardkb import CardKB

# Pyboard : X10=sda, X9=scl
# PYBStick: S3=sda, S5=scl
i2c = I2C(1)
# M5Stack : Grove connector - reduced speed needed
# i2c = I2C(freq=100000, sda=21, scl=22)

keyb = CardKB( i2c )
while True:
	raw = keyb.get_raw()
	if raw != 0:
		print( "Key: %s" % hex(raw) )
