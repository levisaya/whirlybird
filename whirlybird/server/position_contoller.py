__author__ = 'Andy'

import asyncio
import time
from whirlybird.protocols.pilot_input_pb2 import PilotInput
from threading import Event
from whirlybird.server.devices.Adafruit_LSM303 import Adafruit_LSM303


class PositionController(object):
    def __init__(self):
        self.loop = asyncio.get_event_loop()

        self.num_calls = 0
        self.start_time = None
        self.killed = Event()

        self.lsm = Adafruit_LSM303(1)

        pilot_input_handler = asyncio.start_server(self.handle_pilot_input, '', 8888, loop=self.loop)
        self.loop.run_until_complete(pilot_input_handler)
        self.loop.run_until_complete(asyncio.Task(self.position_update()))

    @asyncio.coroutine
    def handle_pilot_input(self, reader, writer):
        while not self.killed.is_set():
            numbytes_buffer = yield from reader.read(1)

            numbytes = ord(numbytes_buffer)

            read_pilot_data = yield from reader.read(numbytes)

            pilot_data = PilotInput()
            try:
                pilot_data.ParseFromString(read_pilot_data)
            except:
                print("Error: Bad Input Message: {}, numbytes: {}".format(read_pilot_data, numbytes))
            else:
                pass

                # Compute desired yaw, pitch and roll.

    @asyncio.coroutine
    def position_update(self):
        current_time = time.time()

        while not self.killed.is_set():
            yield from asyncio.sleep(1)
            lsm_data = self.lsm.read()
            print(lsm_data)
            # new_time = time.time()
            # delta = new_time - current_time
            # if delta > 0.01:
            #     print('Delta: {}'.format(new_time - current_time))
            # current_time = new_time
