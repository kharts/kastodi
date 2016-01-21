# cast_controls.py - implementation of Cast controls dialog
#
# Copyright 2016 kharts (https://github.com/kharts)
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.


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
    """

    def __init__(self, title, thumb):
        super(CastControlsDialog, self).__init__(title)
        self.setGeometry(WINDOW_WIDTH, WINDOW_HEIGHT, NUM_ROWS, NUM_COLUMNS)
        self.thumb = pyxbmct.Image(thumb, aspectRatio=2)
        self.placeControl(self.thumb,
                          row=0,
                          column=0,
                          rowspan=6,
                          columnspan=8)
        self.play_pause_background = pyxbmct.Image(
            filename=image("OSDPauseFO.png"))
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

        info("Hi!")