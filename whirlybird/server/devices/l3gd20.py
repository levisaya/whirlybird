#!/usr/bin/python

# Ported from the Adafruit L3GD20 Arduino library: https://github.com/adafruit/Adafruit_L3GD20


from .i2c import I2c
from enum import Enum

L3gd20Address = 0x6b


class L3gd20Registers(Enum):
    WHO_AM_I = 0x0F         # 11010100 r
    CTRL_REG1 = 0x20        # 00000111 rw
    CTRL_REG2 = 0x21        # 00000000 rw
    CTRL_REG3 = 0x22        # 00000000 rw
    CTRL_REG4 = 0x23        # 00000000 rw
    CTRL_REG5 = 0x24        # 00000000 rw
    REFERENCE = 0x25        # 00000000 rw
    OUT_TEMP = 0x26         # r
    STATUS_REG = 0x27       # r
    OUT_X_L = 0x28          # r
    OUT_X_H = 0x29          # r
    OUT_Y_L = 0x2A          # r
    OUT_Y_H = 0x2B          # r
    OUT_Z_L = 0x2C          # r
    OUT_Z_H = 0x2D          # r
    FIFO_CTRL_REG = 0x2E    # 00000000 rw
    FIFO_SRC_REG = 0x2F     # r
    INT1_CFG = 0x30         # 00000000 rw
    INT1_SRC = 0x31         # r
    TSH_XH = 0x32           # 00000000 rw
    TSH_XL = 0x33           # 00000000 rw
    TSH_YH = 0x34           # 00000000 rw
    TSH_YL = 0x35           # 00000000 rw
    TSH_ZH = 0x36           # 00000000 rw
    TSH_ZL = 0x37           # 00000000 rw
    INT1_DURATION = 0x38    # 00000000 rw


class L3gd20Range(Enum):
    RANGE_250DPS = 0
    RANGE_500DPS = 1
    RANGE_2000DPS = 2


class L3gd20Sensitivity(Enum):
    RANGE_250DPS = 0.00875
    RANGE_500DPS = 0.0175
    RANGE_2000DPS = 0.070


class L3gd20(I2c):
    def __init__(self, range_=L3gd20Range.RANGE_250DPS):
        I2c.__init__(self, L3gd20Address)

        # Normal mode, all 3 channels enabled.
        self.write_8(L3gd20Registers.CTRL_REG1.value, 0x0F)

        # Set the resolution
        self.write_8(L3gd20Registers.CTRL_REG4.value, range_.value << 4)

        self.sensitivity = L3gd20Sensitivity[range_.name].value

    def _check_connected_device(self):
        whoami = self.read_byte(L3gd20Registers.WHO_AM_I.value)

        if whoami in [0xD4, 0xD7]:
            return True, ''
        else:
            return False, 'L3gd20 WHOAMI register returned {}, not 0xD4 or 0xD7'.format(whoami)

    def read(self):
        to_return = {}

        gyro_data = self.read_list(L3gd20Registers.OUT_X_L.value | 0x80, 6)

        for i, axis in enumerate(['x', 'y', 'z']):
            val = gyro_data[i * 2] | (gyro_data[i * 2 + 1] << 8)

            to_return[axis] = val * self.sensitivity

        return to_return

if __name__ == '__main__':
    d = L3gd20(L3gd20Range.RANGE_250DPS)
    import time

    while 1:
        print(d.read())
        time.sleep(1)