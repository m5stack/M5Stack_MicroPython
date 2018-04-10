import os, time, machine

def setup():
    os.chdir('/flash')
    with open("boot.py", "w") as f:
        f.write("""\
# This file is executed on every boot (including wake-boot from deepsleep)
import sys
sys.path[1] = '/flash/lib'

# ---------- M5Cloud ------------
if True:
    from m5stack import lcd, buttonA, buttonB
    if buttonB.isPressed():
        lcd.println('On: OFF-LINE Mode', color=lcd.ORANGE)
    else:
        import wifisetup
        import m5cloud
""")
    
    with open("main.py", "w") as f:
        f.write("""\
from m5stack import lcd

'''
lcd.clear()
lcd.setCursor(0, 0)
lcd.setColor(lcd.WHITE)
lcd.print("Hello world!")
'''
""")

    time.sleep(0.1)
    print('boot.py Creact done! reset..')
    machine.reset()

setup()
