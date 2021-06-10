"""
Test the MicroPython driver for M5Stack U105, DDS unit (AD9833), I2C grove.

Set the frequency (optimized) for a Sine signal

* Author(s):
   29 may 2021: Meurisse D. (shop.mchobby.be) - Initial Writing
"""

from machine import I2C
from mdds import *
from time import sleep_ms

# Pico - I2C(0) - sda=GP8, scl=GP9
i2c = I2C(0)
# M5Stack core
# i2c = I2C( sda=Pin(21), scl=Pin(22) )


dds = DDS(i2c)
# quick_out set & use the freq register 0 & phase register 0
dds.quick_out( SINUS_MODE, freq=10000, phase=0 )

# set_freq() is I2C bus efficient but will reset signal mode to sinus
while True:
	for f in range( 10000, 1000000, 10000 ):
		print( 'Set freq @ %s KHz' % (f//1000) )
		dds.set_freq( reg=0, freq=f )
		sleep_ms(100)
