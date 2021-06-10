"""
mdds.py : MicroPython driver for M5Stack U105, 4 relays I2C grove unit.
* Author(s):
   28 may 2021: Meurisse D. (shop.mchobby.be) - port to MicroPython
				https://github.com/m5stack/M5Stack/tree/master/examples/Unit/DDS_AD9833
"""

__version__ = "0.0.1.0"
__repo__ = "https://github.com/mchobby/esp8266-upy/tree/master/m5stack-u105"

from micropython import const

#define DDS_UNIT_I2CADDR 0x31

DDS_DESC_REG = const(0x10) # Description of interface
DDS_MODE_REG = const(0x20)
DDS_CTRL_REG = const(0x21)
DDS_FREQ_REG = const(0x30)
DDS_PHASE_REG = const(0x34)

DDS_FMCLK = const(10000000)

RESERVED_MODE = const(0)
SINUS_MODE    = const(1)
TRIANGLE_MODE = const(2)
SQUARE_MODE   = const(3)
SAWTOOTH_MODE = const(4)
DC_MODE       = const(5)

DDS_MODES = (RESERVED_MODE, SINUS_MODE, TRIANGLE_MODE, SQUARE_MODE, SAWTOOTH_MODE, DC_MODE)

class DDS:
	""" Drive the DDS AD9833 unit (U105)
		:param i2c: the connected i2c bus machine.I2C
		:param address: the device address; defaults to 0x26 """

	# AD9833 have 2 output reg configurable and user code can set the output
	# with the data coming from output reg 1 / output reg 2

	def __init__(self, i2c, address=0x31):
		self.i2c = i2c
		self.address = address
		self.desc_buf = bytearray(6)
		self.buf2 = bytearray(2)
		self.buf4 = bytearray(4)
		self.buf1 = bytearray(1)
		self.i2c.readfrom_mem_into( self.address, DDS_DESC_REG, self.desc_buf )
		if self.desc_buf != bytes( 'ad9833', 'ASCII' ):
			raise Exception( 'Invalid board description!')

	def set_freq( self, reg, freq ): # uint8_t reg ,uint64_t freq
		""" Change the frequency of signal (will switch back signal to SINUS mode!) """
		assert reg in (0,1), 'invalid freq register!'

		freq = int(freq * 268435456 / DDS_FMCLK)

		self.buf4[0] = (( freq >> 24 ) & 0xff ) | (0xC0 if reg == 1 else 0x80 )
		self.buf4[1] = (( freq >> 16 ) & 0xff )
		self.buf4[2] = (( freq >> 8  ) & 0xff )
		self.buf4[3] = ( freq & 0xff )
		# writeDDSReg(DDS_FREQ_ADDR,sendbuff,4);
		self.i2c.writeto_mem( self.address, DDS_FREQ_REG, self.buf4 )


	def set_phase( self, reg, phase ): # uint8_t reg ,uint32_t phase
		""" Change the phase of the signal """
		assert reg in (0,1), 'invalid phase register!'
		assert 0<= phase <360

		phase = int(phase * 2048 / 360)
		self.buf2[0] = (( phase >> 8 ) & 0xff ) | ( 0xC0 if reg == 1 else 0x80 )
		self.buf2[1] = ( phase & 0xff )

		# writeDDSReg(DDS_PHASE_ADDR,sendbuff,2);
		self.i2c.writeto_mem( self.address, DDS_PHASE_REG, self.buf2 )

	def set_freq_and_phase( self, freg, freq, preg, phase ): #  uint8_t freg, uint64_t freq, uint8_t preg, uint32_t phase
		self.set_freq( freg, freq )
		self.set_phase( preg, phase )

	def mode( self, dds_mode ):
		""" Set the type of WaveForm """
		assert dds_mode in DDS_MODES
		self.buf1[0] = 0x80 | dds_mode
		self.i2c.writeto_mem( self.address, DDS_MODE_REG, self.buf1 )

	#def ctrl( self, ctrlbyte ): # uint8_t
	#	writeDDSReg(DDS_CTRL_ADDR,0x80 | ctrlbyte );
	#	pass

	def select_freq_reg( self, num ): # uint8_t
		""" Which freq reg to activates as output """
		# uint8_t reg = readDDSReg(DDS_CTRL_ADDR);
		self.i2c.readfrom_mem_into( self.address, DDS_CTRL_REG, self.buf1 )
		# reg &= (~0x40);
		self.buf1[0] = self.buf1[0] & (0xFF^0x40)
		# writeDDSReg(DDS_CTRL_ADDR,reg | 0x80 | ( num == 1 ) ? 0x40 : 0 );
		self.buf1[0] = self.buf1[0] | 0x80 | 0x40 if num==1 else 0x00
		self.i2c.writeto_mem( self.address, DDS_CTRL_REG, self.buf1 )

	def select_phase_reg( self, num ): # uint8_t
		""" Which freq reg to activates as output """
		assert num in (0,1)
		# uint8_t reg = readDDSReg(DDS_CTRL_ADDR);
		self.i2c.readfrom_mem_into( self.address, DDS_CTRL_REG, self.buf1 )
		# reg &= (~0x20);
		self.buf1[0] = self.buf1[0] & (0xFF^0x20)
		# writeDDSReg(DDS_CTRL_ADDR, reg | 0x80 | ( num == 1 ) ? 0x20 : 0 );
		self.buf1[0] = self.buf1[0] | 0x80 | 0x20 if num==1 else 0x00
		self.i2c.writeto_mem( self.address, DDS_CTRL_REG, self.buf1 )

	def out( self, freqnum, phasenum): # OUT(uint8_t freqnum,uint8_t phasenum);
		""" Which output regs to activate to the output """
		assert freqnum in (0,1), 'Invalid freqnum!'
		assert phasenum in (0,1), 'Invalid phasenum!'
		#uint8_t reg = readDDSReg(DDS_CTRL_ADDR);
		self.i2c.readfrom_mem_into( self.address, DDS_CTRL_REG, self.buf1 )
		self.buf1[0] = self.buf1[0] & (0xFF^0x60)
		self.buf1[0] = buf1[0] | 0x80 | ( 0x40 if freqnum == 1 else 0x00 ) | ( 0x20 if phasenum == 1 else 0x00 )
		# writeDDSReg(DDS_CTRL_ADDR, reg | 0x80 | (( freqnum == 1 ) ? 0x40 : 0 ) | (( phasenum == 1 ) ? 0x20 : 0 ));
		self.i2c.writeto_mem( self.address, DDS_CTRL_REG, self.buf1 )

	def quick_out( self, dds_mode, freq, phase): # uint64_t freq, uint32_t phase
		""" Quickly set the reg 0 freq, reg 0 phase and activates it as output """
		if dds_mode <= SQUARE_MODE:
			self.set_freq_and_phase( 0,freq, 0,phase )
		self.buf1[0] = 0x80 | dds_mode
		self.i2c.writeto_mem( self.address, DDS_MODE_REG, self.buf1 )
		self.buf1[0] = 0x80 | 0x00
		self.i2c.writeto_mem( self.address, DDS_CTRL_REG, self.buf1 )

	def set_sleep( self, level ): # uint8_t
		assert level in (0,1,2), 'Invalid level!'
		# uint8_t reg = readDDSReg(DDS_CTRL_ADDR);
		self.i2c.readfrom_mem_into( self.address, DDS_CTRL_REG, self.buf1 )
		#reg &= (~0x18);
		self.buf1[0] = self.buf1[0] & (0xFF^0x18)
		#reg |= ( level == 1 ) ? 0x10 : 0;
		self.buf1[0] = self.buf1[0] | (0x10 if level==1 else 0x00 )
		#reg |= ( level == 2 ) ? 0x08 : 0;
		self.buf1[0] = self.buf1[0] | (0x08 if level==2 else 0x00 )
		# writeDDSReg( DDS_CTRL_ADDR, 0x80 | reg );
		self.i2c.writeto_mem( self.address, DDS_CTRL_REG, self.buf1)

	def reset( self ):
		self.buf1[0] = 0x80 | 0x04
		self.i2c.writeto_mem( self.address, DDS_CTRL_REG, self.buf1 )
