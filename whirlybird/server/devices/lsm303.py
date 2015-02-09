#!/usr/bin/python

from .i2c import I2c
from enum import Enum


class Lsm303Addresses(Enum):
    Accelerometer = 0b11001
    Magnetometer = 0b11110


class Lsm303Registers(Enum):
    Control_1 = 0x20
    Control_4 = 0x23
    Accelerometer_out = 0x28
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


class Lsm303(I2c):
    def __init__(self, enable_high_res=False):
        I2c.__init__(self)

        # Enable and set accelerometer resolution.
        self.write_8(Lsm303Addresses.Accelerometer.value,
                     Lsm303Registers.Control_1.value,
                     0x27)
        if enable_high_res:
            self.write_8(Lsm303Addresses.Accelerometer.value,
                         Lsm303Registers.Control_4.value,
                         0b00001000)
        else:
            self.write_8(Lsm303Addresses.Accelerometer.value,
                         Lsm303Registers.Control_4.value,
                         0)
  
        # Enable magnetometer.
        self.write_8(Lsm303Addresses.Magnetometer.value,
                     Lsm303Registers.Magnetometer_enable.value,
                     0x00)

    def read(self):
        to_return = {'accelerometer': {},
                     'magnetometer': {}}
        accelerometer_data = self.read_list(Lsm303Addresses.Accelerometer.value,
                                            Lsm303Registers.Accelerometer_out.value | 0x80,
                                            6)

        for i, axis in enumerate(['x', 'y', 'z']):
            # Swap bytes
            val = accelerometer_data[i * 2] | (accelerometer_data[i * 2 + 1] << 8)

            # Swap to 2's compliment signed
            if val > 32767:
                val -= 65536

            to_return['accelerometer'][axis] = val >> 4

        magnetometer_data = self.read_list(Lsm303Addresses.Magnetometer.value,
                                           Lsm303Registers.Magnetometer_out.value,
                                           6)

        for i, axis in enumerate(['x', 'z', 'y']):
            # Swap bytes
            val = (magnetometer_data[i * 2] << 8) | magnetometer_data[i * 2 + 1]

            # Swap to 2's compliment signed
            if val > 32767:
                val -= 65536

            to_return['magnetometer'][axis] = val

        return to_return

    def set_magnetometer_gain(self, gain):
        self.magnetometer.write_8(Lsm303Addresses.Magnetometer.value,
                                  Lsm303Registers.Magnetometer_gain.value,
                                  gain)


if __name__ == '__main__':
    d = Lsm303()
    import time

    while 1:
        print(d.read())
        time.sleep(1)