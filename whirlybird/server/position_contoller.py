__author__ = 'Andy'

import asyncio
import time
from whirlybird.protocols.pilot_input_pb2 import PilotInput
from threading import Event
from whirlybird.server.devices.Bmp085 import Bmp085
from whirlybird.server.devices.lsm303_accelerometer import Lsm303Accelerometer
from whirlybird.server.devices.lsm303_magnetometer import Lsm303Magnetometer
from whirlybird.server.devices.l3gd20 import L3gd20
from whirlybird.server.devices.adafruit_pwm import AdafruitPwm
from aioprocessing import AioPool, AioQueue, AioEvent, AioProcess
from whirlybird.server.device_polling_process import DevicePollingProcess
from queue import Empty


class PositionController(object):
    def __init__(self):
        self.loop = asyncio.get_event_loop()

        self.num_calls = 0
        self.start_time = None
        self.killed = AioEvent()

        self.sensor_queue = AioQueue()

        self.accelerometer = Lsm303Accelerometer()
        self.magnetometer = Lsm303Magnetometer()
        self.gyro = L3gd20()
        self.baro = Bmp085()
        self.pwm = AdafruitPwm()

        self.baro_reader = DevicePollingProcess(self.baro.get_pressure, self.sensor_queue, self.killed)

        self.baro_reader_process = AioProcess(target=self.baro_reader.read)
        self.baro_reader_process.start()

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
        while not self.killed.is_set():
            start = time.time()
            accelerometer_data = self.accelerometer.read()
            magnetometer_data = self.magnetometer.read()
            gyro_data = self.gyro.read()

            try:
                baro_data = self.sensor_queue.get_nowait()
            except Empty:
                baro_data = None

            print('Accelerometer: {}'.format(accelerometer_data))
            print('Magnetometer: {}'.format(magnetometer_data))
            print('Gyro: {}'.format(gyro_data))
            print('Baro: {}'.format(baro_data))
            print('Time: {}'.format(time.time() - start))