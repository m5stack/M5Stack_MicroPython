import gc
import uos as os

def _boot():
  from m5stack import lcd, buttonA
  import utils
  if buttonA.isPressed():
    if utils.exists('main.py'):
      if utils.exists('_main.py'):
        os.remove('_main.py')
      else:
        os.rename('main.py', '_main.py')
        lcd.println('On: SAFE Mode, ignore run main.py', color=lcd.ORANGE)
  else:
    if not utils.exists('main.py'):
      if utils.exists('_main.py'):
        os.rename('_main.py', 'main.py')
    else:
      if utils.exists('_main.py'):
        os.remove('_main.py')

_boot()
gc.collect()