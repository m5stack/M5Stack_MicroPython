import sys

OFFSET_BOOTLOADER = 0x1000
OFFSET_PARTITIONS = 0x8000
OFFSET_PHY_INIT_DATA = 0xf000 
OFFSET_APPLICATION = 0x10000

files_in = [
    ('bootloader', OFFSET_BOOTLOADER, 'bootloader/bootloader.bin'),
    ('partitions', OFFSET_PARTITIONS, 'partitions_mpy.bin'),
    ('phy_init_data', OFFSET_PHY_INIT_DATA, 'phy_init_data.bin'),
    ('application', OFFSET_APPLICATION, 'MicroPython.bin'),
]
# file_out = sys.argv[1]
file_out = 'firmware.bin'

cur_offset = OFFSET_BOOTLOADER
with open(file_out, 'wb') as fout:
    for name, offset, file_in in files_in:
        assert offset >= cur_offset
        fout.write(b'\xff' * (offset - cur_offset))
        cur_offset = offset
        with open(file_in, 'rb') as fin:
            data = fin.read()
            fout.write(data)
            cur_offset += len(data)
            print('%-12s% 8d' % (name, len(data))) 
    print('%-12s% 8d' % ('total', cur_offset))
