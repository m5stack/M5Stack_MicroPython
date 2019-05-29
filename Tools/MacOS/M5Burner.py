#!/usr/bin/env python
# -*- Coding: utf-8 -*-

from __future__ import print_function
import os, sys
import json
import subprocess
port = '/dev/cu.SLAB_USBtoUART'
baud = 921600
PYTHON_VERSION = os.sys.version_info[0]

# ----- read firmware.json -----
working_dir = os.getcwd()
sub_dir     = 'firmwares'
json_file   = os.path.join(working_dir,sub_dir,'firmware.json')
with open(json_file, 'r') as f:
     fw_list = json.loads(f.read())

# ----- select firmware to write -----
fw_names = [x['name'] for x in fw_list]
for i,x in enumerate(fw_names):
    print(i, x)
try:
    num = int(input('Select No = '))
    if not ( 0 <= num < len(fw_list) ):
        print('Error !')
        exit()
except ValueError:
    print('Error !')
    exit()

path = os.path.join(working_dir, sub_dir, fw_list[num]['path'])
table = {'%port':port, '%baud':str(baud), '%PATH':path, '\\':'/'}
cmds  = ['./tools/esptool.py --chip esp32 --port %port --baud %baud erase_flash']
cmds += ['./tools/esptool.py ' + x for x in fw_list[num]['commands']]
cmd   = '\n'.join(cmds)
for k,v in table.items():
    cmd = cmd.replace(k,v)

# ----- write firmware -----
if PYTHON_VERSION == 3:
    q = input('Write firmware: {0} (y/n) '.format(fw_list[num]['name'])).lower()
elif PYTHON_VERSION == 2:
    q = raw_input('Write firmware: {0} (y/n) '.format(fw_list[num]['name'])).lower()
    cmd = cmd.encode('ascii').replace('\\','/')

cmds = cmd.split('\n')
if q == 'y':
    for cmd in cmds:
        subprocess.call(cmd.split())

exit()
