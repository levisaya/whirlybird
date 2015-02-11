#!/usr/bin/python

from .i2c import I2c
from enum import Enum

Lsm303AccelerometerAddress = 0x19


class Lsm303AccelerometerRegisters(Enum):
    Control_1 = 0x20
    Control_4 = 0x23
    Accelerometer_out = 0x28


class Lsm303Accelerometer(I2c):
    def __init__(self, enable_high_res=False):
        I2c.__init__(self, Lsm303AccelerometerAddress)

        # Enable and set accelerometer resolution.
        self.write_8(Lsm303AccelerometerRegisters.Control_1.value, 0x57)

        if enable_high_res:
            self.write_8(Lsm303AccelerometerRegisters.Control_4.value, 0b00001000)
        else:
            self.write_8(Lsm303AccelerometerRegisters.Control_4.value, 0)

    def _check_connected_device(self):
        # No WHOAMI register, can't check.
        return True, ''

    def read(self):
        to_return = {}
        accelerometer_data = self.read_list(Lsm303AccelerometerRegisters.Accelerometer_out.value | 0x80, 6)

        for i, axis in enumerate(['x', 'y', 'z']):
            # Swap bytes
            val = accelerometer_data[i * 2] | (accelerometer_data[i * 2 + 1] << 8)

            # Swap to 2's compliment signed
            if val > 32767:
                val -= 65536

            to_return[axis] = val >> 4

        return to_return


if __name__ == '__main__':
    d = Lsm303Accelerometer()
    import time

    while 1:
        print(d.read())
        time.sleep(1)