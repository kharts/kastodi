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

    def __init__(self, title, cast, thumb, show_seekbar, percentage=0):
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
        :param percentage: % of already played media
        :type percentage: float
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
        if show_seekbar:
            self.add_seekbar(percentage)
        self.stop_button = pyxbmct.Button(label="Stop casting")
        self.placeControl(self.stop_button,
                          row=9,
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

    def add_seekbar(self, percentage):
        """
        Add seekbar to the dialog window
        :param percentage: number of % of already played media
        :type percentage: float
        :return: None
        """

        self.seek_slider = pyxbmct.Slider()
        self.placeControl(self.seek_slider,
                          row=11,
                          column=0,
                          rowspan=1,
                          columnspan=16)
        max_width = self.seek_slider.getWidth()
        self.progress_bar = ProgressBar(filename=image("progress.png"),
                                        max_width=max_width)
        self.placeControl(self.progress_bar,
                          row=11,
                          column=0,
                          rowspan=1,
                          columnspan=16)
        self.set_percentage(percentage)

    def set_percentage(self, percentage):
        """
        Set percentage of seek_slider and progress_bar
        :param percentage: number of % of already played media
        :type percentage: float
        :return: None
        """

        debug("percentage: " + str(percentage))
        self.seek_slider.setPercent(percentage)
        self.progress_bar.setPercent(percentage)

    def update_percentage(self):
        """
        Update percentage of seekbar (seek_slider and progress_bar)
        :return: None
        """

        self.cast.media_controller.update_status(blocking=True)
        if self.cast.media_controller.status.duration:
            current_time = self.cast.media_controller.status.current_time
            total_time = self.cast.media_controller.status.duration
            percentage = current_time / total_time * 100
        else:
            percentage = 0
        debug("percentage: " + str(percentage))
        self.set_percentage(percentage)

    def onAction(self, Action):
        """
        onAction event handler
        :param Action: action type
        :type Action: xbmcgui.Action
        :return: None
        """

        debug("Action: " + str(Action.getId()))
        for volume_action in VOLUME_ACTIONS:
            if Action == volume_action:
                focused_control = self.getFocus()
                if focused_control == self.volume_slider:
                    self.set_volume()
        self.update_percentage()
        super(CastControlsDialog, self).onAction(Action)


class ProgressBar(xbmcgui.ControlImage):
    """
    Control which displays progress bar.
    Implements interface of standart xbmcgui.ControlProgress,
    but it works indeed
    """

    def __new__(cls, *args, **kwargs):
        filename = kwargs.get("filename", "")
        return super(ProgressBar, cls).__new__(cls, -10, -10, 1, 1, filename)

    def __init__(self, filename, max_width):
        """
        :param filename: path to image file
        :type filename: str
        :param max_width: maximum width of the progress bar
        :type max_width: int
        :return: None
        """

        self.MAX_WIDTH = max_width

    def getPercent(self):
        """
        Get a float of the percent of the progress
        :return: percent of the progress
        :rtype: float
        """

        return 100.0 * self.getWidth() / self.MAX_WIDTH

    def setPercent(self, percent):
        """
        Set a percentage of the progressbar to show
        :param percent: percentage to show
        :type percent: float
        :return: None
        """

        width = int(self.MAX_WIDTH * percent / 100.0)
        self.setWidth(width)