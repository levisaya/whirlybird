__author__ = 'Andy'

import time
from whirlybird.server.position_contoller import PositionController

if __name__ == "__main__":
    position_controller = PositionController()

    position_controller.run()

    time.sleep(10)

    position_controller.kill()