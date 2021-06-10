""" CardKB, Mini I2C Keyboard - readkey on keyboardover I2C

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

MOD_TEXT = { MOD_NONE : 'none', MOD_SYM : 'SYMBOL', MOD_FN : 'FUNCTION'}

keyb = CardKB( i2c )

# Ctrl key as text
CTRL_NAME = {0xB5:'UP',0xB4:'LEFT',0xB6:'DOWN',0xB7:'RIGHT',0x1B:'ESC',0x09:'TAB',0x08:'BS',0x7F:'DEL',0x0D:'CR'}

print( 'Keycode | Ascii | Modifier' )
print( '---------------------------')
while True:
	keycode,ascii,modifier = keyb.read_key()
	if keycode == None:
		continue # restart the loop
	if keyb.is_ctrl( keycode ): # Ctrl char cannot be displayed safely!!!
		if keycode in CTRL_NAME:
			ascii = CTRL_NAME[keycode]
		else: # we do not know the name for that KeyCode
			ascii = 'ctrl' # so we replace it with "ctrl" string

	print( "  %5s | %5s | %s" %(hex(keycode), ascii, MOD_TEXT[modifier]) )
