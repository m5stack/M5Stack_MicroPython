esptool.py --chip esp32 --port /dev/tty.SLAB_USBtoUART --baud 961200 write_flash -z 0x1000 ~/workspace/M5Stack/M5Cloud/firmwares/m5cloud-20180309-v0.3.6.bin
ampy put SFArch_48.fon && ampy put main.py