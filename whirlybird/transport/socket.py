__author__ = 'Andy'

import socket


class SocketTransport(object):
    def __init__(self, address, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((address, port))

    def emit(self, buffer):
        self.sock.sendall(bytes([len(buffer)]) + buffer)