#!/usr/bin/python

from .i2c import I2c
from enum import Enum

Lsm303MagnetometerAddress = 0x1E


class Lsm303MagnetometerRegisters(Enum):
    Magnetometer_gain = 0x01
    Magnetometer_enable = 0x02
    Magnetometer_out = 0x03


class MagnetometerGain(Enum):
    Gain_1_3 = 0x20
    Gain_1_9 = 0x40
    Gain_2_5 = 0x60
    Gain_4_0 = 0x80
    Gain_4_7 = 0xA0
    Gain_5_6 = 0xC0
    Gain_8_1 = 0xE0


class Lsm303Magnetometer(I2c):
    def __init__(self):
        I2c.__init__(self, Lsm303MagnetometerAddress)

        # Enable magnetometer.
        self.write_8(Lsm303MagnetometerRegisters.Magnetometer_enable.value, 0x00)

    def _check_connected_device(self):
        # No WHOAMI register, can't check.
        return True, ''

    def read(self):
        to_return = {}

        magnetometer_data = self.read_list(Lsm303MagnetometerRegisters.Magnetometer_out.value, 6)

        for i, axis in enumerate(['x', 'z', 'y']):
            val = (magnetometer_data[i * 2] << 8) | magnetometer_data[i * 2 + 1]

            # Swap to 2's compliment signed
            if val > 32767:
                val -= 65536

            to_return[axis] = val

        return to_return

    def set_magnetometer_gain(self, gain):
        self.magnetometer.write_8(Lsm303MagnetometerRegisters.Magnetometer_gain.value, gain)


if __name__ == '__main__':
    d = Lsm303Magnetometer()
    import time

    while 1:
        print(d.read())
        time.sleep(1)