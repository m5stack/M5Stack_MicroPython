"""
Test the MicroPython driver for M5Stack U105, DDS unit (AD9833), I2C grove.

Iterate through the common Signal (note that SAWTOOTH have fixed freq of 55.9 Hz)

* Author(s):
   29 may 2021: Meurisse D. (shop.mchobby.be) - Initial Writing
"""

from machine import I2C
from mdds import *
from time import sleep

# Pico - I2C(0) - sda=GP8, scl=GP9
i2c = I2C(0)
# M5Stack core
# i2c = I2C( sda=Pin(21), scl=Pin(22) )

shapes = ( SINUS_MODE, TRIANGLE_MODE, SQUARE_MODE, SAWTOOTH_MODE )
shape_names = { SINUS_MODE : "Sinus", TRIANGLE_MODE : "Triangle",
                SQUARE_MODE : "Square", SAWTOOTH_MODE : "SawTooth"}
dds = DDS(i2c)

while True:
	for shape in shapes:
		print( '%s @ 10 KHz' % shape_names[shape] )
		dds.quick_out( shape, freq=10000, phase=0 )
		sleep( 1 )
