# cast_controls.py - implementation of Cast controls dialog
#
# Copyright 2016 kharts (https://github.com/kharts)
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.


import pyxbmct
from common import *


class CastControlsDialog(pyxbmct.AddonDialogWindow):
    """
    Class for implementing Cast controls dialog - window with
    play/pause/stop buttons, seekbar, volume control etc.
    """

    def __init__(self, title, thumb):
        super(CastControlsDialog, self).__init__(title)
        self.setGeometry(640, 480, 6, 8)
        self.thumb = pyxbmct.Image(thumb)
        self.placeControl(self.thumb,
                          row=0,
                          column=0,
                          rowspan=6,
                          columnspan=8)
        self.play_pause_background = pyxbmct.Image(filename=image("OSDPauseFO.png"))
        self.placeControl(self.play_pause_background,
                          row=2,
                          column=3,
                          rowspan=2,
                          columnspan=2)
        # self.play_pause_button = pyxbmct.RadioButton(
        #     label="",
        #     focusOnTexture=image("OSDPauseFO.png"),
        #     noFocusOnTexture=image("OSDPauseNF.png"),
        #     focusOffTexture=image("OSDPlayFO.png"),
        #     noFocusOffTexture=image("OSDPlayNF.png"))
        #self.placeControl(self.play_pause_button, 1, 1)