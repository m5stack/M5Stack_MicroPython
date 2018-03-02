import uos, time, machine

def setup():
    uos.chdir('/flash')
    with open("boot.py", "w") as f:
        f.write("""\
# This file is executed on every boot (including wake-boot from deepsleep)
import sys
sys.path[1] = '/flash/lib'

# ---------- M5Cloud ------------
M5Cloud_Enable = True

if M5Cloud_Enable:
    from m5stack import lcd, buttonA, buttonB
    if buttonB.isPressed():
        lcd.println('On: OFF-LINE Mode', color=lcd.ORANGE)
    elif not buttonA.isPressed():
        lcd.println('On: M5Cloud Mode', color=0xCCCCCC)
        import wifisetup
        import m5cloud
""")
    
    with open("main.py", "w") as f:
        f.write("""\
from m5stack import lcd

#lcd.clear()
#lcd.print("Hello world!")
""")

    time.sleep(0.1)
    print('boot.py Creact done! reset..')
    machine.reset()

setup()
