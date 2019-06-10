import utils
import uos as os
import utime as time
import display as lcd
import machine, ubinascii
from ubutton import Button
from micropython import const
from machine import Timer

tex = Timer(0)
tex.init(mode = tex.EXTBASE)

_BUTTON_A_PIN = const(39)
_BUTTON_B_PIN = const(38)
_BUTTON_C_PIN = const(37)
_SPEAKER_PIN  = const(25)
# ------------------------------------------------------------------------------- #
class Speaker:
  def __init__(self, pin=25, volume=5):
    self.pwm = machine.PWM(machine.Pin(pin), freq = 1, duty = 0, timer = 2)
    self._timer = None
    self._volume = volume
    self._beat_time = 500
    self._timer = machine.Timer(8)
    self._timer.init(period=10, mode=self._timer.ONE_SHOT, callback=self._timeout_cb)   

  def _timeout_cb(self, timer):
    self.pwm.duty(0)
    time.sleep_ms(1)
    self.pwm.freq(1)
    self._timer.stop()

  def tone(self, freq=1800, duration=200, timer=True, volume=None):
    if volume == None:
      self.pwm.init(freq=freq, duty=self._volume)
    else:
      self.pwm.init(freq=freq, duty=volume)
    duration = max(0, duration)
    if timer:
      if self._timer.isrunning():
        self._timer.period(duration)
      else:
        self._timer.init(period=duration, mode=self._timer.ONE_SHOT, callback=self._timeout_cb)   
      time.sleep_ms(duration-15)
    else:
      time.sleep_ms(duration)
      self.pwm.duty(0)
      time.sleep_ms(1)
      self.pwm.freq(1)
    

  def sing(self, freq=1800, beat=1, end=True, volume=None):
    self.tone(freq, int(beat*self._beat_time), end, volume)
  
  def set_beat(self, value=120):
    self._beat_time = int(60000 / value)

  def volume(self, val):
    self._volume = val


def fimage(x, y, file, type=1):
  if file[:3] == '/sd':
    utils.filecp(file, '/flash/fcache', blocksize=8192)
    lcd.image(x, y, '/flash/fcache', 0, type)
    os.remove('/flash/fcache')
  else:
    lcd.image(x, y, file, 0, type)

def delay(ms):
  time.sleep_ms(ms)


def map_value(value, input_min, input_max, aims_min, aims_max):
  value = min(max(input_min, value), input_max)
  value_deal = (value - input_min) * (aims_max - aims_min) / (input_max - input_min) + aims_min
  return round(value_deal, 2)

# ------------------ M5Stack -------------------
# Node ID
node_id = ubinascii.hexlify(machine.unique_id()).decode('utf-8')
print('\nDevice ID:' + node_id)
print('LCD initializing...', end='')

# pin Analog and digital

# LCD
lcd = lcd.TFT()
lcd.init(lcd.M5STACK, width=240, height=320, speed=40000000, rst_pin=33, 
         miso=19, mosi=23, clk=18, cs=14, dc=27, bgr=True,invrot=3, 
         expwm=machine.PWM(32, duty=0, timer=1))
lcd.setBrightness(30)
lcd.clear()
lcd.setColor(0xCCCCCC)
print('Done!')


#BUTTON
m5button = Button()
buttonA = m5button.register(_BUTTON_A_PIN)
buttonB = m5button.register(_BUTTON_B_PIN)
buttonC = m5button.register(_BUTTON_C_PIN)

# SPEAKER
speaker = Speaker()

# ----------------------- for flow----------------------------------------- #
def wait(s):
  if s > 0.02:
    for i in range(int(s / 0.01)):
      time.sleep_ms(10)
  else:
    time.sleep(s)
# ---------------------------------------------------------------- #
