__author__ = 'Andy'

from whirlybird.protocols import pilot_input_pb2


class InputDriverBase(object):
    def __init__(self, transport):
        self.transport = transport

    def _to_integer(self, value):
        return int(value * 255 + 255)

    def emit(self,
             left_stick_x,
             left_stick_y,
             right_stick_y,
             right_stick_x,
             triggers):
        to_emit = pilot_input_pb2.PilotInput()
        to_emit.left_stick_x = self._to_integer(left_stick_x)
        to_emit.left_stick_y = self._to_integer(left_stick_y)
        to_emit.right_stick_y = self._to_integer(right_stick_y)
        to_emit.right_stick_x = self._to_integer(right_stick_x)
        to_emit.triggers = self._to_integer(triggers)

        # print('LX: {}, LY: {}, RX: {}, RY: {}, Trigger: {}'. format(to_emit.left_stick_x,
        #                                                             to_emit.left_stick_y,
        #                                                             to_emit.right_stick_x,
        #                                                             to_emit.right_stick_y,
        #                                                             to_emit.triggers))

        self.transport.emit(to_emit.SerializeToString())
