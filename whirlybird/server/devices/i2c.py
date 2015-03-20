#!/usr/bin/python

__author__ = 'Andy'

import smbus
from functools import partial


class I2c(object):
    def __init__(self, address, i2c_bus=1):
        self.bus = smbus.SMBus(i2c_bus)

        self.write_8 = partial(self.bus.write_byte_data, *[address])
        self.write_16 = partial(self.bus.write_word_data, *[address])
        self.write_byte = partial(self.bus.write_byte, *[address])
        self.write_list = partial(self.bus.write_i2c_block_data, *[address])
        self.read_list = partial(self.bus.read_i2c_block_data, *[address])
        self.read_byte = partial(self.bus.read_byte_data, *[address])
        self.read_short = partial(self.bus.read_word_data, *[address])

        connected_ok, error = self._check_connected_device()
        if not connected_ok:
            raise Exception('Failed to connect to device at {}: {}'.format(address, error))

    def read_16(self, reg):
        bytes = self.read_list(reg, 2)
        return (bytes[0] << 8) | bytes[1]

    def read_s16(self, reg):
        val = self.read_16(reg)

        if val > 32767:
            val -= 65536
        return val


    def _check_connected_device(self):
        raise NotImplementedError('_check_connected_device must be implemented by the derived class.')