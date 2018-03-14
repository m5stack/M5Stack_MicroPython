from utime import ticks_ms

# EVENT_IS_PRESSED = const(0x01)
# EVENT_WAS_PRESSED = const(0x02)
# EVENT_WAS_RELEASED = const(0x04)
# EVENT_RELEASED_FOR = const(0x08)

class Button:

  def __init__(self, pin, dbtime=50):
    from machine import Pin
    self._pin = Pin(pin)
    self._pin.init(Pin.IN)
    self._pin.irq(trigger=(Pin.IRQ_FALLING|Pin.IRQ_RISING), handler=self.irq_cb)
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
        if ticks_ms() - self._timeshoot > self._dbtime:
          self._lastState = True
          self._startTicks = ticks_ms()
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
            if ticks_ms() - self._startTicks > self._timeout:
              self._event |= 0x08  # EVENT_RELEASED_FOR
              if self._releasedFor_cb:
                self._releasedFor_cb()
      self._timeshoot = ticks_ms()


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
    if self._lastState and ticks_ms() - self._startTicks > timeout * 1000:
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



# ------------- Example -------------

# buttonA = Button(39)
# buttonB = Button(38)
# buttonC = Button(37)


# # Callback
# def on_wasPressed():
#   print('Button A was Pressed.')
  
# def on_wasReleased():
#   print('Button A was Released.')

# def on_releasedFor():
#   print('Button A released for 1.2s press hold.')
  
# buttonC.wasPressed(on_wasPressed)
# buttonC.wasReleased(on_wasReleased)
# buttonC.releasedFor(1.2, on_releasedFor)



# # Loop 
# while True:
#   if buttonB.wasPressed():
#     print('Button B was Pressed')

#   if buttonB.wasReleased():
#     print('Button B was Released')

#   if buttonB.pressedFor(1.5):
#     print('Button B pressed for 1.5s')

#   if buttonB.releasedFor(1.5):
#     print('Button B released for 1.5s press hold.')
    
#   sleep(0.1)
