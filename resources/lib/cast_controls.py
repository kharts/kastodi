# cast_controls.py - implementation of Cast controls dialog
#
# Copyright 2016 kharts (https://github.com/kharts)
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.


import xbmcgui
import pyxbmct
from common import *


WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
NUM_ROWS = 12
NUM_COLUMNS = 16
VOLUME_ACTIONS = [xbmcgui.ACTION_MOUSE_WHEEL_DOWN,
                  xbmcgui.ACTION_MOUSE_WHEEL_UP,
                  xbmcgui.ACTION_MOUSE_DRAG]

class CastControlsDialog(pyxbmct.AddonDialogWindow):
    """
    Class for implementing Cast controls dialog - window with
    play/pause/stop buttons, seekbar, volume control etc.

    :param title: text for window header
    :type title: str
    :param thumb: path to thumbnail of currently playing video.
        Will be set as background of content part of the window
    :type thumb: str
    """

    def __init__(self, title, cast, thumb, show_seekbar):
        """
        :param title: text for window header
        :type title: str
        :param cast: connected cast device
        :type cast: pychromecast.Chromecast
        :param thumb: path to thumbnail of currently playing video.
            Will be set as background of content part of the window
        :type thumb: str
        :param show_seekbar: show slider for seeking to the given
            position of the media
        :type show_seekbar: bool
        """

        super(CastControlsDialog, self).__init__(title)
        self.cast = cast
        self.setGeometry(WINDOW_WIDTH, WINDOW_HEIGHT, NUM_ROWS, NUM_COLUMNS)
        self.thumb = pyxbmct.Image(thumb, aspectRatio=2)
        self.placeControl(self.thumb,
                          row=0,
                          column=0,
                          rowspan=12,
                          columnspan=16)
        self.playing = True
        self.pause_button = pyxbmct.Button(
            label="",
            focusTexture=image("pauseFO.png"),
            noFocusTexture=image("pauseNF.png")
        )
        self.placeControl(self.pause_button,
                          row=4,
                          column=6,
                          rowspan=4,
                          columnspan=4)
        self.connect(self.pause_button, self.pause_button_pressed)
        self.play_button = pyxbmct.Button(
            label="",
            focusTexture=image("playFO.png"),
            noFocusTexture=image("playNF.png")
        )
        self.placeControl(self.play_button,
                          row=4,
                          column=6,
                          rowspan=4,
                          columnspan=4)
        self.play_button.setVisible(False)
        self.connect(self.play_button, self.play_button_pressed)
        stop_button_shift = 1
        if show_seekbar:
            self.seekbar = pyxbmct.Slider()
            self.placeControl(self.seekbar,
                              row=11,
                              column=0,
                              rowspan=1,
                              columnspan=16)
        self.stop_button = pyxbmct.Button(label="Stop casting")
        self.placeControl(self.stop_button,
                          row=8,
                          column=12,
                          rowspan=2,
                          columnspan=4)
        self.connect(self.stop_button, self.close)
        self.volume_icon = pyxbmct.Image(image("VolumeIcon.png"))
        self.placeControl(self.volume_icon,
                          row=0,
                          column=14,
                          rowspan=1,
                          columnspan=1)
        self.volume_slider = pyxbmct.Slider()
        self.placeControl(self.volume_slider,
                          row=1,
                          column=13,
                          rowspan=1,
                          columnspan=3)
        if self.cast.status:
            self.volume_slider.setPercent(self.cast.status.volume_level * 100)
        else:
            self.volume_slider.setPercent(100)

    def pause_button_pressed(self):
        """
        pause_button pressing handler
        :return: None
        """

        self.playing = False
        if not self.cast.media_controller.is_playing:
            return
        self.cast.media_controller.pause()
        self.pause_button.setVisible(False)
        self.play_button.setVisible(True)
        self.setFocus(self.play_button)

    def play_button_pressed(self):
        """
        play_button pressing hanlder
        :return: None
        """

        self.playing = True
        if self.cast.media_controller.is_playing:
            return
        self.cast.media_controller.play()
        self.play_button.setVisible(False)
        self.pause_button.setVisible(True)
        self.setFocus(self.pause_button)

    def set_volume(self):
        """
        Set volume respecting to value of volume_slider
        :return: None
        """

        volume = self.volume_slider.getPercent() / 100
        self.cast.set_volume(volume)

    def onAction(self, Action):
        """
        onAction event handler
        :param Action: action type
        :type Action: xbmcgui.Action
        :return: None
        """

        for volume_action in VOLUME_ACTIONS:
            if Action == volume_action:
                focused_control = self.getFocus()
                if focused_control == self.volume_slider:
                    self.set_volume()
        super(CastControlsDialog, self).onAction(Action)

