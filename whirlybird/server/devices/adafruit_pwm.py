#!/usr/bin/python

import time
import math
from whirlybird.server.devices.i2c import I2c
from enum import Enum

AdafruitPwmAddress = 0x40


class AdafruitPwmRegisters(Enum):
    Mode1 = 0x00
    Mode2 = 0x01
    Subaddr1 = 0x02
    Subaddr2 = 0x03
    Subaddr3 = 0x04
    Prescale = 0xFE
    Led0OnL = 0x06
    Led0OnH = 0x07
    Led0OffL = 0x08
    Led0OffH = 0x09
    AllLedOnL = 0xFA
    AllLedOnH = 0xFB
    AllLedOffL = 0xFC
    AllLedOffH = 0xFD


class AdafruitPwmBits(Enum):
    Restart = 0x80
    Sleep = 0x10
    AllCall = 0x01
    Invert = 0x10
    OutDrv = 0x04


class AdafruitPwm(I2c):
    def __init__(self, address=AdafruitPwmAddress):
        I2c.__init__(self, address)

        self.set_all_pwm(0, 0)
        self.write_8(AdafruitPwmRegisters.Mode2.value, AdafruitPwmBits.OutDrv.value)
        self.write_8(AdafruitPwmRegisters.Mode1.value, AdafruitPwmBits.AllCall.value)

        # Wait for oscillator
        time.sleep(0.005)

        mode1 = self.read_byte(AdafruitPwmRegisters.Mode1.value)

        # wake up (reset sleep)
        mode1 &= ~AdafruitPwmBits.Sleep.value
        self.write_8(AdafruitPwmRegisters.Mode1.value, mode1)

        # Wait for oscillator
        time.sleep(0.005)

    def _check_connected_device(self):
        return True, ''

    def set_pwm_frequency(self, frequency):
        prescaleval = 25000000.0    # 25MHz
        prescaleval /= 4096.0       # 12-bit
        prescaleval /= float(frequency)
        prescaleval -= 1.0
        prescale = math.floor(prescaleval + 0.5)

        old_mode = self.read_byte(AdafruitPwmRegisters.Mode1.value)

        # go to sleep
        new_mode = (old_mode & 0x7F) | AdafruitPwmBits.Sleep.value
        self.write_8(AdafruitPwmRegisters.Mode1.value, new_mode)

        self.write_8(AdafruitPwmRegisters.Prescale.value, int(math.floor(prescale)))
        self.write_8(AdafruitPwmRegisters.Mode1.value, old_mode)
        time.sleep(0.005)
        self.write_8(AdafruitPwmRegisters.Mode1.value, old_mode | AdafruitPwmBits.Restart.value)

    def set_pwm(self, channel, on, off):
        self.write_8(AdafruitPwmRegisters.Led0OnL.value + 4 * channel, on & 0xFF)
        self.write_8(AdafruitPwmRegisters.Led0OnH.value + 4 * channel, on >> 8)
        self.write_8(AdafruitPwmRegisters.Led0OffL.value + 4 * channel, off & 0xFF)
        self.write_8(AdafruitPwmRegisters.Led0OffH.value + 4 * channel, off >> 8)

    def set_all_pwm(self, on, off):
        self.write_8(AdafruitPwmRegisters.AllLedOnL.value, on & 0xFF)
        self.write_8(AdafruitPwmRegisters.AllLedOnH.value, on >> 8)
        self.write_8(AdafruitPwmRegisters.AllLedOffL.value, off & 0xFF)
        self.write_8(AdafruitPwmRegisters.AllLedOffH.value, off >> 8)

if __name__ == '__main__':
    pwm = AdafruitPwm()

    servo_min = 150  # Min pulse length out of 4096
    servo_max = 600  # Max pulse length out of 4096

    pwm.set_pwm_frequency(60)

    while 1:
        pwm.set_pwm(0, 0, servo_min)
        time.sleep(1)
        pwm.set_pwm(0, 0, servo_max)
        time.sleep(1)
