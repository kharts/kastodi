# kastodi.py - main module of the addon
#
# Copyright 2016 kharts (https://github.com/kharts)
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.

import xbmc
import xbmcgui
from common import *


IDLE_TIME = 1 # 1 second
PLAYER_CONTROLS_ID = 10114 # player controls window ID
WINDOW_OSD = 12901 # video on screen display window ID

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

        #info("onPlayBackStarted")
        self.add_cast_button()


    def add_cast_button(self):
        """
        Add Cast button to player
        :return: None
        """

        # test_button = xbmcgui.ControlButton(x=50,
        #                                     y=50,
        #                                     width=100,
        #                                     height=100,
        #                                     label="Cast")
        cast_button = xbmcgui.ControlImage(x=50,
                                           y=50,
                                           width=72,
                                           height=72,
                                           filename=image("ic_cast_white24dp.png"))
        player_window = xbmcgui.Window(WINDOW_OSD)
        #player_window = xbmcgui.WindowDialog()
        player_window.addControl(cast_button)
        #player_window.doModal()
        cast_button.setVisible(True)
        #xbmc.executebuiltin("ActivateWindow(" + PLAYER_CONTROLS_ID + ")")


if __name__ == "__main__":
    run()
