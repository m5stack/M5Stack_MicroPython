"""
m4relay.py : MicroPython driver for M5Stack U097, 4 relays I2C grove unit.
* Author(s):
   28 may 2021: Meurisse D. (shop.mchobby.be) - port to MicroPython
				https://github.com/m5stack/M5Stack/blob/master/examples/Unit/4-RELAY/4-RELAY.ino
"""

__version__ = "0.0.1.0"
__repo__ = "https://github.com/mchobby/esp8266-upy/tree/master/m5stack-u097"

from micropython import const


SYS_CTRL = const(0x10) # System control
IO_CTRL  = const(0X11) # Relay_ctrl_mode_reg


class Relays:
	""" Drive the 4-Relays unit (U097)
		:param i2c: the connected i2c bus machine.I2C
		:param address: the device address; defaults to 0x26 """

	def __init__(self, i2c, address=0x26):
		self.i2c = i2c
		self.address = address
		self.io_buf = bytearray(1) # LED & Relay states
		self.buf1 = bytearray(1)

		self.synchronize( True )
		self.io_buf[0] = 0x00 # set all off
		self.i2c.writeto_mem( self.address, IO_CTRL, self.io_buf )

	def synchronize( self, synch = True ):
		""" Synchronize the Relay and the LED, switch on the relay will also switch the LED """
		self.buf1[0] = 0x01 if synch else 0x00
		self.i2c.writeto_mem( self.address, SYS_CTRL, self.buf1 )

	def relay( self, index, state ):
		""" Change the state of the relay """
		assert 0<= index <=3, 'Invalid relay index'
		if state:
			self.io_buf[0] |= (1<<index)
		else:
			self.io_buf[0] &= 0xFF ^ (1<<index)

		self.i2c.writeto_mem( self.address, IO_CTRL, self.io_buf )

	def led( self, index, state ):
		""" Change the state of the led (only for synchronize False) """
		assert 0<= index <=3, 'Invalid led index'
		if state:
			self.io_buf[0] |= (1<<(index+4))
		else:
			self.io_buf[0] &= 0xFF ^ (1<<(index+4))

		self.i2c.writeto_mem( self.address, IO_CTRL, self.io_buf )
