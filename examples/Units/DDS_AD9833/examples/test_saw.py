"""
Test the MicroPython driver for M5Stack U105, DDS unit (AD9833), I2C grove.

Set SAWTOOTH signal output (this have fixed frequency)

* Author(s):
   30 may 2021: Meurisse D. (shop.mchobby.be) - Initial Writing
"""

from machine import I2C
from mdds import *
from time import sleep

# Pico - I2C(0) - sda=GP8, scl=GP9
i2c = I2C(0)
# M5Stack core
# i2c = I2C( sda=Pin(21), scl=Pin(22) )

dds = DDS(i2c)

# Generates the SAW TOOTH signal at 55.9Hz (fixed frequency)
dds.quick_out( SAWTOOTH_MODE, freq=1, phase=0 )
