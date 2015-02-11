#!/usr/bin/python

__author__ = 'Andy'

import smbus
from functools import partial


class I2c(object):
    def __init__(self, address):
        i2c_bus = 1
        with open('/proc/cpuinfo', 'r') as cpuinfo:
            for line in cpuinfo:
                if line.startswith('Revision'):
                    i2c_bus = 1 if line.rstrip()[-1] in ['2', '3'] else 0
                    break
        self.bus = smbus.SMBus(i2c_bus)

        self.write_8 = partial(self.bus.write_byte_data, *[address])
        self.write_16 = partial(self.bus.write_word_data, *[address])
        self.write_byte = partial(self.bus.write_byte, *[address])
        self.write_list = partial(self.bus.write_i2c_block_data, *[address])
        self.read_list = partial(self.bus.read_i2c_block_data, *[address])
        self.read_byte = partial(self.bus.read_byte_data, *[address])
        self.read_short = partial(self.bus.read_word_data, *[address])