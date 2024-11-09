"""
Test the MicroPython driver for M5Stack U105, DDS unit (AD9833), I2C grove.

Set the frequency for any Sine, Square, Triangle signal

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
dds.quick_out( TRIANGLE_MODE, freq=10000, phase=0 )

# on not sinusoidal waveform, quick_out() must be used to change the frequency
while True:
	for f in range( 10000, 100000, 10000 ):
		print( 'Set freq @ %s KHz' % (f//1000) )
		dds.quick_out( TRIANGLE_MODE, freq=f, phase=0 )
		sleep_ms(100)
	for f in range( 100000, 10000, -10000 ):
		print( 'Set freq @ %s KHz' % (f//1000) )
		dds.quick_out( TRIANGLE_MODE, freq=f, phase=0 )
		sleep_ms(100)
