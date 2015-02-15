#!/usr/bin/python

# Ported from the Adafruit BMP085 Arduino library: https://github.com/adafruit/Adafruit_BMP085_Unified


from .i2c import I2c
from enum import Enum

Bmp085Address = 0x77


class Bmp085Registers(Enum):
    CAL_AC1 = 0xAA      # R Calibration data (16 bits)
    CAL_AC2 = 0xAC      # R Calibration data (16 bits)
    CAL_AC3 = 0xAE      # R Calibration data (16 bits)
    CAL_AC4 = 0xB0      # R Calibration data (16 bits)
    CAL_AC5 = 0xB2      # R Calibration data (16 bits)
    CAL_AC6 = 0xB4      # R Calibration data (16 bits)
    CAL_B1 = 0xB6       # R Calibration data (16 bits)
    CAL_B2 = 0xB8       # R Calibration data (16 bits)
    CAL_MB = 0xBA       # R Calibration data (16 bits)
    CAL_MC = 0xBC       # R Calibration data (16 bits)
    CAL_MD = 0xBE       # R Calibration data (16 bits)
    CHIPID = 0xD0
    VERSION = 0xD1
    SOFTRESET = 0xE0
    CONTROL = 0xF4
    TEMPDATA = 0xF6
    PRESSUREDATA = 0xF6


class Bmp085Commands(Enum):
    READTEMPCMD = 0x2E
    READPRESSURECMD = 0x34


class Bmp085Mode(Enum):
    ULTRALOWPOWER = 0
    STANDARD = 1
    HIGHRES = 2
    ULTRAHIGHRES = 3


class Bmp085(I2c):
    def __init__(self,
                 mode=Bmp085Mode.ULTRAHIGHRES,
                 use_datasheet_calibrations=False):
        I2c.__init__(self, Bmp085Address)

        self.mode = mode.value

        if use_datasheet_calibrations:
            self.coefficients = {
                'ac1': 408,
                'ac2': -72,
                'ac3': -14383,
                'ac4': 32741,
                'ac5': 32757,
                'ac6': 23153,
                'b1': 6190,
                'b2': 4,
                'mb': -32768,
                'mc': -8711,
                'md': 2868
            }
        else:
            self.coefficients = {
                'ac1': self.read_s16(Bmp085Registers.CAL_AC1.value),
                'ac2': self.read_s16(Bmp085Registers.CAL_AC2.value),
                'ac3': self.read_s16(Bmp085Registers.CAL_AC3.value),
                'ac4': self.read_16(Bmp085Registers.CAL_AC4.value),
                'ac5': self.read_16(Bmp085Registers.CAL_AC5.value),
                'ac6': self.read_16(Bmp085Registers.CAL_AC6.value),
                'b1': self.read_s16(Bmp085Registers.CAL_B1.value),
                'b2': self.read_s16(Bmp085Registers.CAL_B2.value),
                'mb': self.read_s16(Bmp085Registers.CAL_MB.value),
                'mc': self.read_s16(Bmp085Registers.CAL_MC.value),
                'md': self.read_s16(Bmp085Registers.CAL_MD.value)
            }

    def _check_connected_device(self):
        chip_id = self.read_byte(Bmp085Registers.CHIPID.value)

        if chip_id == 0x55:
            return True, ''
        else:
            return False, 'Bmp085 CHIPID register returned {}, not 0x55'.format(chip_id)

    def compute_b5(self, raw_temp):
        x1 = ((raw_temp - self.coefficients['ac6']) * self.coefficients['ac5']) >> 15
        x2 = (self.coefficients['mc'] << 11) // (x1 + self.coefficients['md'])
        return x1 + x2

    def _read_raw_temp(self):
        self.write_8(Bmp085Registers.CONTROL.value, Bmp085Commands.READTEMPCMD.value)

        time.sleep(0.05)

        return self.read_16(Bmp085Registers.TEMPDATA.value)

    def read_temp(self):
        raw_temp = self._read_raw_temp()
        b5 = self.compute_b5(raw_temp)
        return ((b5 + 8) >> 4) / 10

if __name__ == '__main__':
    d = Bmp085(use_datasheet_calibrations=False)
    import time

    while 1:
        print(d.read_temp())
        time.sleep(1)