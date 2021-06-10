""" CardKB, Mini I2C Keyboard - simplistic read char over I2C

Author(s):
* Meurisse D for MC Hobby sprl

See Github: https://github.com/mchobby/esp8266-upy/tree/master/cardkb
"""

from machine import I2C
from cardkb import *

# Pyboard : X10=sda, X9=scl
# PYBStick: S3=sda, S5=scl
i2c = I2C(1)
# M5Stack : Grove connector - reduced speed needed
# i2c = I2C(freq=100000, sda=21, scl=22)

s = ''

keyb = CardKB( i2c )
while True:
	ch = keyb.read_char( wait=True ) # Wait for a key to be pressed (by default)
	if ord(ch) == RETURN:
		print( 'Return pressed! Blank string')
		s = ''
	elif ord(ch) == BACKSPACE:
		s = s[:-1] # remove last char
	else:
		s = s + ch # Add the char to the string
	print( s )
