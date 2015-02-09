__author__ = 'Andy'

import pygame
from whirlybird.client.input_drivers.input_driver_base import InputDriverBase


class Xbox360Controller(InputDriverBase):
    def __init__(self, transport):
        InputDriverBase.__init__(self, transport)
        pygame.joystick.init()
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()

    def compute(self):
        left_analog_x = self.joystick.get_axis(0)
        left_analog_y = self.joystick.get_axis(1)

        right_analog_x = self.joystick.get_axis(3)
        right_analog_y = self.joystick.get_axis(4)

        triggers = self.joystick.get_axis(2)

        self.emit(left_analog_x,
                  left_analog_y,
                  right_analog_x,
                  right_analog_y,
                  triggers)






