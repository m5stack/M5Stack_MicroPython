# Using the U097 "I2C 4 relays" (Grove connector) with MicroPython

The "[U097: 4-Relay Unit](https://shop.m5stack.com/products/4-relay-unit)" from M5Stack is a 4 relays module that can be controlled via I2C. This unit fits a Grove connector to ease the connection on Grove's compatible plateforms.

![U097: 4 relays unit](docs/_static/u097.jpg)

It is possible to add Grove to your favorit plateform by wiring your own connector with a  [Grove to Pin](https://shop.mchobby.be/product.php?id_product=2145) (or [Grove to Pad](https://shop.mchobby.be/product.php?id_product=1929
)).

__Remarks:__
This driver is sourced from [esp8266-upy GitHub](https://github.com/mchobby/esp8266-upy) maintained by [MCHobby](http://shop.mchobby.be)

# Wire

## Wire to Pico

![U097 to pico](docs/_static/u097-to-pico.jpg)

## Wire to M5Stack Core

![U097 to core](docs/_static/u097-to-core.jpg)

# Test

First, copy the library [lib/m4relay.py](lib/m4relay.py) on your plateform. Then you can execute the examples scripts.

The [test_simple.py](examples/test_simple.py) script (visible here below) explains hos to contole the U097 relays.

``` python
from machine import I2C
from m4relay import Relays
from time import sleep

# Pico - I2C(0) - sda=GP8, scl=GP9
i2c = I2C(0)
# M5Stack core
# i2c = I2C( sda=Pin(21), scl=Pin(22) )

rel = Relays(i2c)

# The LED is controled with the Relay

# Switch all relay ON
for i in range(4): # from 1 to 3
	rel.relay( i, True )
	sleep( 1 )

# Switch All relay OFF
for i in range(4): # from 1 to 3
	rel.relay( i, False )
	sleep( 1 )
```

The [test_async.py](examples/test_async.py) script would allows to control :
* the LEDs with `Relays.led(index=0..3, state=True/False)` and
* the Relays with  `Relays.relay(index=0..3, state=True/False)`

... independantly from each other when LEDs and Relays are desynchronized with ( `Relays.synchronize( False )` ).

