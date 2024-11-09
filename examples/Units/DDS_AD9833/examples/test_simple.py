"""
Test the MicroPython driver for M5Stack U105, DDS unit (AD9833), I2C grove.

Set a 10 KHz Sinewave

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

dds = DDS(i2c)

freq = 10000 # 10 KHz
phase = 0
dds.quick_out( SINUS_MODE, freq, phase )
