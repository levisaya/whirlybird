__author__ = 'Andy'


class DevicePollingProcess(object):
    def __init__(self, poll_fn, output_queue, kill_event):
        self.poll_fn = poll_fn
        self.output_queue = output_queue
        self.kill_event = kill_event

    def read(self):
        while not self.kill_event.is_set():
            self.output_queue.put(self.poll_fn())