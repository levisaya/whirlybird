#!/usr/bin/python

# Ported from the Adafruit BMP085 Arduino library: https://github.com/adafruit/Adafruit_BMP085_Unified


from .i2c import I2c
from enum import Enum
import math

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

        self.mode_delay = {Bmp085Mode.ULTRALOWPOWER: 0.05,
                           Bmp085Mode.STANDARD: 0.08,
                           Bmp085Mode.HIGHRES: 0.14,
                           Bmp085Mode.ULTRAHIGHRES: 0.26}[mode]

        self.use_datasheet_calibrations = use_datasheet_calibrations

        if self.use_datasheet_calibrations:
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
        if self.use_datasheet_calibrations:
            return 27898
        else:
            self.write_8(Bmp085Registers.CONTROL.value, Bmp085Commands.READTEMPCMD.value)

            time.sleep(0.05)

            return self.read_16(Bmp085Registers.TEMPDATA.value)

    def get_temperature(self):
        raw_temp = self._read_raw_temp()
        b5 = self.compute_b5(raw_temp)
        return ((b5 + 8) >> 4) / 10

    def _read_raw_pressure(self):
        if self.use_datasheet_calibrations:
            return 23843
        else:
            self.write_8(Bmp085Registers.CONTROL.value, Bmp085Commands.READPRESSURECMD.value)

            time.sleep(self.mode_delay)

            pressure = (self.read_16(Bmp085Registers.PRESSUREDATA.value) << 8) + \
                        self.read_byte(Bmp085Registers.PRESSUREDATA.value + 2)

            pressure >>= (8 - self.mode)

            return pressure

    def get_pressure(self):
        ut = self._read_raw_temp()
        up = self._read_raw_pressure()

        # Temperature compensation
        b5 = self.compute_b5(ut)

        # Pressure compensation
        b6 = b5 - 4000
        x1 = (self.coefficients['b2'] * ((b6 * b6) >> 12)) >> 11
        x2 = (self.coefficients['ac2'] * b6) >> 11
        x3 = x1 + x2
        b3 = (((self.coefficients['ac1'] * 4 + x3) << self.mode) + 2) >> 2
        x1 = (self.coefficients['ac3'] * b6) >> 13
        x2 = (self.coefficients['b1'] * ((b6 * b6) >> 12)) >> 16
        x3 = ((x1 + x2) + 2) >> 2
        b4 = (self.coefficients['ac4'] * (x3 + 32768)) >> 15
        b7 = ((up - b3) * (50000 >> self.mode))

        if b7 < 0x80000000:
            p = (b7 << 1) // b4
        else:
            p = (b7 // b4) << 1

        x1 = (p >> 8) * (p >> 8)
        x1 = (x1 * 3038) >> 16
        x2 = (-7357 * p) >> 16
        return (p + ((x1 + x2 + 3791) >> 4)) / 100

    @staticmethod
    def pressure_to_altitude(atmospheric, sealevel=1013.25):
        return 44330.0 * (1.0 - pow(atmospheric / sealevel, 0.1903))

    @staticmethod
    def sealevel_for_altitude(altitude, atmospheric):
        return atmospheric / math.pow(1.0 - (altitude/44330.0), 5.255)

if __name__ == '__main__':
    d = Bmp085(use_datasheet_calibrations=False)
    import time

    while 1:
        print(d.pressure_to_altitude(d.get_pressure()))
        time.sleep(1)