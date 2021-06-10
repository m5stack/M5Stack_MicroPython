"""
Test the MicroPython driver for M5Stack U097, 4 relays I2C grove unit.

In SYNC mode, the LED is controled by the RELAY state

* Author(s):
   28 may 2021: Meurisse D. (shop.mchobby.be) - port to MicroPython
				https://github.com/m5stack/M5Stack/blob/master/examples/Unit/4-RELAY/4-RELAY.ino
"""

from machine import I2C
from m4relay import Relays
from time import sleep

# Pico - I2C(0) - sda=GP8, scl=GP9
i2c = I2C(0)
# M5Stack core
# i2c = I2C( sda=Pin(21), scl=Pin(22) )

rel = Relays(i2c)

# The LED is controled with the Relay

# Switch all relay ON
for i in range(4): # from 1 to 3
	rel.relay( i, True )
	sleep( 1 )

# Switch All relay OFF
for i in range(4): # from 1 to 3
	rel.relay( i, False )
	sleep( 1 )
