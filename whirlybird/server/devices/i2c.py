#!/usr/bin/python

__author__ = 'Andy'

import smbus


class I2c(object):
    def __init__(self):
        i2c_bus = 1
        with open('/proc/cpuinfo', 'r') as cpuinfo:
            for line in cpuinfo:
                if line.startswith('Revision'):
                    i2c_bus = 1 if line.rstrip()[-1] in ['2', '3'] else 0
                    break
        self.bus = smbus.SMBus(i2c_bus)

        self.write_8 = self.bus.write_byte_data
        self.write_16 = self.bus.write_word_data
        self.write_byte = self.bus.write_byte
        self.write_list = self.bus.write_i2c_block_data
        self.read_list = self.bus.read_i2c_block_data
        self.read_byte = self.bus.read_byte_data
        self.read_short = self.bus.read_word_data