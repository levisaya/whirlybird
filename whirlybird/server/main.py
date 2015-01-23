__author__ = 'Andy'

import socketserver


class ProtocolHandler(socketserver.StreamRequestHandler):
    def handle(self):
        while True:
            data = self.rfile.readline().strip()
            print("{} wrote: {}".format(self.client_address[0], data))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8888

    # Create the server, binding to localhost on port 9999
    server = socketserver.TCPServer((HOST, PORT), ProtocolHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()