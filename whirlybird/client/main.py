__author__ = 'Andy'

import pygame
import pygame.display

from whirlybird.transport.socket import SocketTransport

import os

# set SDL to use the dummy NULL video driver,
#   so it doesn't need a windowing system.
os.environ["SDL_VIDEODRIVER"] = "dummy"

from whirlybird.client.input_drivers.xbox_360 import Xbox360Controller

def main():
    #some platforms might need to init the display for some parts of pygame.

    pygame.display.init()
    screen = pygame.display.set_mode((1,1))

    protocol = SocketTransport('192.168.1.113', 8888)

    controller = Xbox360Controller(protocol)
    clock = pygame.time.Clock()
    FPS = 60

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        controller.compute()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
    pygame.quit()