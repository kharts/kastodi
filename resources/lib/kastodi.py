# kastodi.py - main module of the addon


import xbmc
import xbmcgui
from common import *


IDLE_TIME = 1 # 1 second
PLAYER_CONTROLS_ID = 10114 # player controls window ID


def run():
    """
    Main function of the addon
    :return: None
    """

    player = CustomPlayer()

    monitor = xbmc.Monitor()

    while not monitor.abortRequested():
        if monitor.waitForAbort(IDLE_TIME):
            # Abort was requested while waiting. We should exit
            break


class CustomPlayer(xbmc.Player):
    """ Class for catching Player events"""

    def onPlayBackStarted(self):
        """
        Start when players playback is started
        :return: None
        """

        info("onPlayBackStarted")
        test_button = xbmcgui.ControlButton(x=50,
                                            y=50,
                                            width=100,
                                            height=100,
                                            label="Cast")
        #player_window = xbmcgui.Window(PLAYER_CONTROLS_ID)
        player_window = xbmcgui.Window()
        player_window.addControl(test_button)
        player_window.show()
        test_button.setVisible(True)


if __name__ == "__main__":
    run()
