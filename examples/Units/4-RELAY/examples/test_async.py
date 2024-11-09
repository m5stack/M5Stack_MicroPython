"""
Test ASYNC mode the MicroPython driver for M5Stack U097, 4 relays I2C grove unit.

In ASYNC mode, the LED can be controled independantly from the relays

* Author(s):
   28 may 2021: Meurisse D. (shop.mchobby.be) - port to MicroPython
				https://github.com/m5stack/M5Stack/blob/master/examples/Unit/4-RELAY/4-RELAY.ino
"""

from machine import I2C
from m4relay import Relays
from time import sleep_ms, sleep

# Pico - I2C(0) - sda=GP8, scl=GP9
i2c = I2C(0)
# M5Stack core
# i2c = I2C( sda=Pin(21), scl=Pin(22) )

rel = Relays(i2c)

# The LED is controled independantly
rel.synchronize( False )

# blink leds
def blink_leds():
	global rel
	for count in range( 10 ):
		for i in range( 4 ):
			rel.led(i,True)
		sleep_ms(100)
		for i in range( 4 ):
			rel.led(i,False)
		sleep_ms(100)


# Switch all relay ON
for i in range(4): # from 1 to 3
	rel.relay( i, True )
	blink_leds();
	sleep( 1 )

# Switch All relay OFF
for i in range(4): # from 1 to 3
	rel.relay( i, False )
	blink_leds()
	sleep( 1 )
