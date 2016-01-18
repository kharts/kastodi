# kastodi.py - main module of the addon
#
# Copyright 2016 kharts (https://github.com/kharts)
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.


import sys
import os
import mimetypes
import urllib
import xbmc
import xbmcgui
from common import *


# add resources/lib folder to path variable
# (for importing pychromecast and zeroconf)
addon_path = xbmc.translatePath(this_addon.getAddonInfo("path"))
lib_path = os.path.join(addon_path, "resources", "lib")
sys.path.insert(0, lib_path)
debug(sys.path)
import pychromecast
debug("pychromecast is imported successfully")

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
        player.check_cast_button_visibility()
        #thread = threading.Thread(target=player.check_cast_button_visibility)
        #thread.start()
        if monitor.waitForAbort(IDLE_TIME):
            # Abort was requested while waiting. We should exit
            break


class CustomPlayer(xbmc.Player):
    """ Class for catching Player events"""

    def __init__(self):
        super(CustomPlayer, self).__init__()
        self.player_window = PlayerWindow()

    def onPlayBackStarted(self):
        """
        Start when players playback is started
        :return: None
        """

        self.add_cast_button()

    def add_cast_button(self):
        """
        Add Cast button to player
        :return: None
        """

        #player_window = PlayerWindow(WINDOW_OSD)
        #self.player_window = PlayerWindow()
        self.player_window.add_cast_button()
        #player_window.doModal()
        #player_window.show()
        #player_window.cast_button.setVisible(False)

    def check_cast_button_visibility(self):
        """
        Check if Cast button visibility needs to be changed
        :return: None
        """

        condition = "Window.IsVisible(" + str(WINDOW_OSD) + ")"
        video_osd_visible = xbmc.getCondVisibility(condition)
        debug("video_osd_visible: " + str(video_osd_visible))
        debug("player_window.visible: " + str(self.player_window.visible))
        if video_osd_visible:
            if not self.player_window.visible:
                self.player_window.show_window()
        else:
            if self.player_window.visible:
                self.player_window.hide_window()


class PlayerWindow(xbmcgui.WindowDialog):
    """
    Class for extending Player Window by placing Cast button
    """
    
    def __init__(self):
        super(PlayerWindow, self).__init__()
        self.visible = False
        self.cast_button = None

    def add_cast_button(self):
        """
        Add Cast button to Video OSD window
        :return: None
        """

        if not self.cast_button:
            self.cast_button = xbmcgui.ControlButton(
                x=50,
                y=50,
                width=72,
                height=72,
                label="",
                focusTexture=image("ic_cast_blue_24dp.png"),
                noFocusTexture=image("ic_cast_white_24dp.png"))
            self.addControl(self.cast_button)
            self.cast_button.setVisible(True)
            # condition = "Window.IsVisible(" + str(WINDOW_OSD) + ")"
            # self.cast_button.setVisibleCondition(condition)

    def show_window(self):
        """
        Show dialog window
        :return: None
        """

        debug("show_window")
        #self.cast_button.setVisible(True)
        #self.doModal()
        self.show()
        self.visible = True
        debug("visible = True")

    def hide_window(self):
        """
        Hide dialog window
        :return: None
        """

        debug("hide_window")
        #self.cast_button.setVisible(False)
        self.close()
        self.visible = False

    def onClick(self, controlId):
        """
        "onClick" event handler
        :param controlId: id of the source of the event
        :type control: xbmcgui.Control
        :return: None
        """

        #info("Click")
        debug("onClick")
        if self.cast_button:
            if controlId == self.cast_button.getId():
                #info("Click on cast_button")
                #self.cast_button_pressed()
                pass

    def onControl(self, control):
        """
        onControl event handler
        :param control: source of the event
        :type control: xbmcgui.Control
        :return: None
        """

        debug("onControl")
        #info("Some control is pressed")
        if control == self.cast_button:
            #info("Cast button is pressed")
            self.cast_button_pressed()

    def cast_button_pressed(self):
        """
        Handle click on Cast button
        :return: None
        """

        progress_dialog = xbmcgui.DialogProgress()
        progress_dialog.create("Discovering cast devices...")
        chromecasts = pychromecast.get_chromecasts_as_dict().keys()
        if progress_dialog.iscanceled():
            progress_dialog.close()
            return
        progress_dialog.close()
        if not chromecasts:
            info("No cast devices connected")
            return
        select_chromecast_dialog = xbmcgui.Dialog()
        index = select_chromecast_dialog.select("Cast to",
                                                chromecasts)
        cast_name = chromecasts[index]
        progress_dialog.create("Connecting to " + cast_name + "...")
        self.start_casting(cast_name)
        progress_dialog.close()

    def start_casting(self, chromecast_name):
        """
        Start casting to the Chromecast with the given friendly name
        :param chromecast_name: friendly name of selected Chromecast
        :type chromecast_name: str
        :return: None
        """

        cast = pychromecast.get_chromecast(friendly_name=chromecast_name)
        if not cast:
            error("Couldn't connect to " + chromecast_name)
            return
        cast.wait()
        url = self.get_playing_url()
        debug("url: " + url)
        content_type, encoding = mimetypes.guess_type(url)
        if not content_type:
            content_type = get_content_type(url)
        debug("content_type: " + str(content_type))
        if not xbmc.getCondVisibility("Player.Paused()"):
            xbmc.Player().pause()
        cast.media_controller.play_media(url,
                                         content_type)

    def get_playing_url(self):
        """
        Get URL of currently playing media
        :return: url of the media
        :rtype: str
        """

        player = xbmc.Player()
        return player.getPlayingFile()


def get_content_type(url):
    """
    Get content type of the resource given by url
    :param url: address of the resource
    :type: str
    :return: content-type in the form "type/subtype"
    :rtype: str
    """

    try:
        response = urllib.urlopen(url)
    except Exception, e:
        log_exception(str(e))
        return None
    return response.info().type


if __name__ == "__main__":
    run()
