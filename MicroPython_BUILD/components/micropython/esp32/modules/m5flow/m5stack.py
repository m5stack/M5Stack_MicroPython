import uos as os
import utime as time
import display as lcd
import machine, ubinascii
from ubutton import Button
from micropython import const

_BUTTON_A_PIN = const(39)
_BUTTON_B_PIN = const(37)
# ------------------------------------------------------------------------------- #

def delay(ms):
  time.sleep_ms(ms)

def map_value(value, input_min, input_max, aims_min, aims_max):
  value_deal = value * (aims_max - aims_min) / (input_max - input_min) + aims_min
  value_deal = value_deal if value_deal < aims_max else aims_max
  value_deal = value_deal if value_deal > aims_min else aims_min
  return value_deal

# ------------------ M5Stack -------------------
# Node ID
node_id = ubinascii.hexlify(machine.unique_id()).decode('utf-8')
print('\nDevice ID:' + node_id)
print('LCD initializing...')

# pin Analog and digital
import axp192
axp = axp192.Axp192()
axp.powerAll()

# LCD
lcd = lcd.TFT()
lcd.init(lcd.M5STICK, speed=30000000, bgr=True, mosi=15, miso=36, clk=13, cs=5, dc=23, rst_pin=18, width=80, height=160)

#BUTTON
m5button = Button()
buttonA = m5button.register(_BUTTON_A_PIN)
buttonB = m5button.register(_BUTTON_B_PIN)