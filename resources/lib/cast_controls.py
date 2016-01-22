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
NUM_ROWS = 6
NUM_COLUMNS = 8


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

    def __init__(self, title, thumb):
        """
        :param title: text for window header
        :type title: str
        :param thumb: path to thumbnail of currently playing video.
        Will be set as background of content part of the window
        :type thumb: str
        """

        super(CastControlsDialog, self).__init__(title)
        self.setGeometry(WINDOW_WIDTH, WINDOW_HEIGHT, NUM_ROWS, NUM_COLUMNS)
        self.thumb = pyxbmct.Image(thumb, aspectRatio=2)
        self.placeControl(self.thumb,
                          row=0,
                          column=0,
                          rowspan=6,
                          columnspan=8)
        self.playing = True
        self.play_pause_background = pyxbmct.Image(
            filename=image("OSDPauseNF.png"))
        self.placeControl(self.play_pause_background,
                          row=2,
                          column=3,
                          rowspan=2,
                          columnspan=2)
        self.play_pause_button = pyxbmct.Button(
            label="",
            focusTexture="",
            noFocusTexture="")
        self.placeControl(self.play_pause_button,
                          row=2,
                          column=3,
                          rowspan=2,
                          columnspan=2)
        self.connect(self.play_pause_button, self.play_pause_button_pressed)

    def play_pause_button_pressed(self):
        """
        onClick handle of play_pause_button
        :return:
        """

        self.playing = not self.playing
        self.set_play_pause_background(self.play_pause_button.getId())

    def set_play_pause_background(self, focused_control_id):
        """
        Set background for play_pause_button control
        :param focused_control_id: id of currently focused control
        :type focused_control_id: int
        :return: None
        """

        if self.playing:
            if focused_control_id == self.play_pause_button.getId():
                self.play_pause_background.setImage(image("OSDPauseFO.png"))
            else:
                self.play_pause_background.setImage(image("OSDPauseNF.png"))
        else:
            if focused_control_id == self.play_pause_button.getId():
                self.play_pause_background.setImage(image("OSDPlayFO.png"))
            else:
                self.play_pause_background.setImage(image("OSDPlayNF.png"))

    def onFocus(self, controlId):
        """
        onFocus event handler of the window
        :param controlId: id of the currently focused control
        :type controlId: int
        :return: None
        """

        self.set_play_pause_background(controlId)

    def onAction(self, Action):
        """
        onAction event handler of the window
        :param Action: action performed
        :type Action: xbmcgui.Action
        :return: None
        """

        if Action == xbmcgui.ACTION_MOUSE_MOVE:
            focusedId = self.getFocusId()
            self.set_play_pause_background(focusedId)
        super(CastControlsDialog, self).onAction(Action)