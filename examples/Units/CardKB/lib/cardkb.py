""" CardKB, Mini I2C Keyboard - driver for MicroPython

Author(s):
* Meurisse D for MC Hobby sprl
* M5Stack for Arduino version

See Github: https://github.com/mchobby/esp8266-upy/tree/master/cardkb
"""

__version__ = "0.0.1"
__repo__ = "https://github.com/mchobby/esp8266-upy"

ESC = 0x1B
BACKSPACE = 0x08
DEL    = 0x7F
TAB    = 0x09
CR     = 0x0D
RETURN = 0x0D
LF     = 0x10

LEFT  = 0xB4
RIGHT = 0xB7
UP    = 0xB5
DOWN  = 0xB6

FN_LEFT  = 0x98
FN_RIGHT = 0xA5
FN_UP    = 0x99
FN_DOWN  = 0xA4

MOD_NONE = 0x00 # no modifier applyed
MOD_FN   = 0x01 # FUNCTION modifier
MOD_SYM  = 0x02 # SYMBOL modifier

class CardKB:
	def __init__( self, i2c, address=0x5F ):
		self.i2c = i2c
		self.address = address
		self.buf1 = bytearray(1)

	def get_raw( self ):
		""" Read raw value from CardKb. Return 0x00 if no key pressed otherwise returns the hex key value """
		self.i2c.readfrom_into( self.address, self.buf1 )
		return self.buf1[0]

	def is_ascii( self, data ):
		""" Check is the data is supported to be an ascii char (including ESCAPE, BACKSPACE, ETC) """
		# See https://upload.wikimedia.org/wikipedia/commons/d/dd/ASCII-Table.svg
		return (0x20 <= data <= 0x7E) or (data in (ESC,BACKSPACE,DEL,TAB,CR,LF))

	def is_ctrl( self, data ):
		""" Check is the data contains a control character  """
		return (0 <= data <= 31) or (data == 127) or self.is_arrow(data)

	def is_sym( self, data ):
		""" Is the key symb key """
		return data in (33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 45, 47, 58, 59, 61, 63, 64, 91, 92, 93, 94, 95, 96, 123, 124, 125, 126)

	def is_fn( self, data ):
		""" Is a FN key """
		return (data != 0x97) and (0x80<=data<=0xAF)

	def is_arrow( self, data ):
		""" Is an arrow key? """
		return data in (UP,DOWN,RIGHT,LEFT,FN_UP,FN_DOWN,FN_RIGHT,FN_LEFT)

	def decode_arrow( self, data ):
		# Decode the arrow and possibly returns the modifier
		if data in (UP,DOWN,RIGHT,LEFT):
			return (data, MOD_NONE) # No modifier
		else:
			if data == FN_UP:
				return (UP, MOD_FN)
			elif data == FN_DOWN:
				return (DOWN, MOD_FN)
			elif data == FN_RIGHT:
				return (RIGHT, MOD_FN)
			elif data == FN_LEFT:
				return (LEFT, MOD_FN)

	def read_char( self, wait=True ):
		""" read an ASCII character from the keyboard. Wait until the key is pressed (otherwise, return None) """
		self.get_raw() # value available in buf1
		if self.is_ascii( self.buf1[0] ):
			return chr( self.buf1[0] )
		elif not(wait):
			return None
		else: # wait for a char
		 	while True:
				self.get_raw()
				if self.is_ascii( self.buf1[0] ):
					return chr( self.buf1[0] )

	def read_key( self ):
		""" Returns the (keycode, ascii/None, modifier) or (None,None,None) if no key pressed. """
		keycode = self.get_raw()
		if keycode == 0x00:
			return (None,None,None)
		ascii = None
		mod   = MOD_NONE # Modifier

		if self.is_arrow(keycode):
			keycode, mod = self.decode_arrow( keycode )
			return keycode,ascii,mod

		if self.is_ascii( keycode ):
			ascii = chr( keycode )

		if self.is_sym( keycode ):
			mod = MOD_SYM
		elif self.is_fn( keycode ):
			mod = MOD_FN
		return (keycode, ascii, mod)
