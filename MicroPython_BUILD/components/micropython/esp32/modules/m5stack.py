from micropython import const
import os, time, machine, ubinascii
import display as lcd
import utils

VERSION = "v0.3.9"

_BUTTON_A_PIN = const(39)
_BUTTON_B_PIN = const(38)
_BUTTON_C_PIN = const(37)
_SPEAKER_PIN  = const(25)


class Button:

  def __init__(self, pin, dbtime=50):
    from machine import Pin
    self._pin = Pin(pin)
    self._pin.init(Pin.IN)
    self._pin.irq(self.irq_cb, (Pin.IRQ_FALLING|Pin.IRQ_RISING))
    self._wasPressed_cb = None
    self._wasReleased_cb = None
    self._releasedFor_cb = None
    self._timeshoot = 0
    self._dbtime = dbtime
    self._lastState = False
    self._startTicks = 0
    self._timeout = 0
    self._event = 0


  def irq_cb(self, pin):
    pin_val = pin.value()
    if self._pin == pin:
      # FALLING
      if pin_val == 0:  
        if time.ticks_ms() - self._timeshoot > self._dbtime:
          self._lastState = True
          self._startTicks = time.ticks_ms()
          self._event |= 0x02  # EVENT_WAS_PRESSED
          if self._wasPressed_cb:
            self._wasPressed_cb()
      # RISING
      elif pin_val == 1:
        if self._lastState == True:
          self._lastState = False
          self._event |= 0x04  # EVENT_WAS_RELEASED
          if self._wasReleased_cb:
            self._wasReleased_cb()
          if self._timeout > 0:
            if time.ticks_ms() - self._startTicks > self._timeout:
              self._event |= 0x08  # EVENT_RELEASED_FOR
              if self._releasedFor_cb:
                self._releasedFor_cb()
      self._timeshoot = time.ticks_ms()


  def read(self):
    return not self._pin.value()


  def isPressed(self):
    return self.read()
  

  def isReleased(self):
    return not self.read()
      

  def wasPressed(self, callback=None):
    if callback == None:
      if (self._event & 0x02) > 0: # EVENT_WAS_PRESSED
        self._event -= 0x02
        return True
      else:
        return False
    else:
      self._wasPressed_cb = callback


  def wasReleased(self, callback=None):
    if callback == None:
      if (self._event & 0x04 ) > 0: # EVENT_WAS_RELEASED
        self._event -= 0x04
        return True
      else:
        return False
    else:
      self._wasReleased_cb = callback
  

  def pressedFor(self, timeout):
    if self._lastState and time.ticks_ms() - self._startTicks > timeout * 1000:
      return True
    else:
      return False


  def releasedFor(self, timeout, callback=None):
    self._timeout = timeout * 1000 # second
    if callback == None:
      if (self._event & 0x08) > 0: # EVENT_RELEASED_FOR
        self._event -= 0x08
        return True
      else:
        return False
    else:
      self._releasedFor_cb = callback


class Speaker:
  def __init__(self, pin=25, volume=2):
    self.pwm = machine.PWM(machine.Pin(pin), 1, 0, 0)
    self._timer = 0
    self._volume = volume*10

  def _timeout_cb(self, timer):
    self._timer.deinit()
    self.pwm.duty(0)
    self.pwm.deinit()

  def tone(self, freq=1800, timeout=200):
    self.pwm.init(freq=freq, duty=self._volume)
    if timeout > 0:
      self._timer = machine.Timer(3)
      self._timer.init(period=timeout, mode=self._timer.ONE_SHOT, callback=self._timeout_cb)   

  def volume(self, val):
    self._volume = val * 10


def fimage(x, y, file, type=1):
  if file[:3] == '/sd':
    utils.filecp(file, '/flash/fcache', blocksize=8192)
    lcd.image(x, y, '/flash/fcache', 0, type)
    os.remove('/flash/fcache')
  else:
    lcd.image(x, y, file, 0, type)


def delay(ms):
  time.sleep_ms(ms)


# ------------------ M5Stack -------------------

# Node ID
node_id = ubinascii.hexlify(machine.unique_id()).decode('utf-8')
print('\nDevice ID:' + node_id)


# LCD
lcd = lcd.TFT()
lcd.init(lcd.M5STACK, width=240, height=320, speed=27000000, rst_pin=33, backl_pin=32, miso=19, mosi=23, clk=18, cs=14, dc=27, bgr=True, backl_on=1, invrot=3)
lcd.clear()
lcd.setBrightness(500)
lcd.setColor(0xCCCCCC)
lcd.println('M5Stack MicroPython '+VERSION, 0, 0)
lcd.println('Device ID:'+node_id)
lcd.println('Boot Mode:')
lcd.println('Hold button A to boot into SAFE mode.')
lcd.println('Hold button B to boot into OFFLINE mode.')


# BUTTON
buttonA = Button(_BUTTON_A_PIN)
buttonB = Button(_BUTTON_B_PIN)
buttonC = Button(_BUTTON_C_PIN)


# SPEAKER
speaker = Speaker()
