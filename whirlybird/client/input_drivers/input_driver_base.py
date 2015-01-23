__author__ = 'Andy'

from whirlybird.protocols import pilot_input_pb2


class InputDriverBase(object):
    def __init__(self, transport):
        self.transport = transport

    def emit(self,
             left_stick_x,
             left_stick_y,
             right_stick_y,
             right_stick_x,
             triggers):
        to_emit = pilot_input_pb2.PilotInput()
        to_emit.left_stick_x = left_stick_x
        to_emit.left_stick_y = left_stick_y
        to_emit.right_stick_y = right_stick_y
        to_emit.right_stick_x = right_stick_x
        to_emit.triggers = triggers
        self.transport.emit(to_emit.SerializeToString())
