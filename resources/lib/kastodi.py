# kastodi.py - main module of the addon


import xbmc
from common import *


idle_time = 1 # 1 second


def run():
    """
    Main function of the addon
    :return: None
    """

    player = CustomPlayer()

    monitor = xbmc.Monitor()

    while not monitor.abortRequested():
        if monitor.waitForAbort(idle_time):
            # Abort was requested while waiting. We should exit
            break


class CustomPlayer(xbmc.Player):
    """ Class for catching Player events"""

    def onPlayBackStarted(self):
        """
        Start when players playback is started
        :return: None
        """

        debug("onPlayBackStarted")


if __name__ == "__main__":
    run()
