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
import shutil
from xml.etree import ElementTree as ET
import json
import xbmc
import xbmcgui
import xbmcaddon
from common import *
from cast_controls import CastControlsDialog


# add resources/lib folder to path variable
# (for importing pychromecast and zeroconf)
addon_path = xbmc.translatePath(this_addon.getAddonInfo("path"))
lib_path = os.path.join(addon_path, "resources", "lib")
sys.path.insert(0, lib_path)
debug(sys.path)
import pychromecast
import zeroconf
import netifaces

IDLE_TIME = 1 # 1 second
NEED_RESTART = False
TRIES = int(this_addon.getSetting("tries")) # Number of connection attempts
CAST_BUTTON_START_TEXT = "<!-- kastodi_start -->"
CAST_BUTTON_END_TEXT = "<!-- kastodi_end -->"

pychromecast.IGNORE_CEC.append('*')  # Ignore CEC on all devices


def cast_button_pressed():
    """
    Function is called when user is pressing Cast button
    :return: None
    """

    progress_dialog = xbmcgui.DialogProgress()
    progress_dialog.create("Discovering cast devices...")
    chromecasts = pychromecast.get_chromecasts_as_dict(tries=TRIES).keys()
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
    start_casting(cast_name)


def start_casting(chromecast_name):
    """
    Start casting to the Chromecast with the given friendly name
    :param chromecast_name: friendly name of selected Chromecast
    :type chromecast_name: str
    :return: None
    """

    progress_dialog = xbmcgui.DialogProgress()
    progress_dialog.create("Connecting to " + chromecast_name + "...")
    cast = pychromecast.get_chromecast(friendly_name=chromecast_name,
                                       tries=TRIES)
    if not cast:
        error("Couldn't connect to " + chromecast_name)
        return
    cast.wait()
    player = xbmc.Player()
    url = player.getPlayingFile()
    debug("url: " + url)
    url = transform_url(url)
    debug("transformed url: " + str(url))
    if not url:
        return
    content_type, encoding = mimetypes.guess_type(url)
    if not content_type:
        content_type = get_content_type(url)
    debug("content_type: " + str(content_type))
    title = get_playing_title() #xbmc.getInfoLabel("Player.Title")
    thumb = xbmc.getInfoLabel("Player.Art(thumb)")
    thumb_url = transform_url(thumb, show_warnings=False)
    debug("thumb_url: " + str(thumb_url))
    metadata = {'metadataType': 0,
                'title': title,
                'images': [{'url': thumb_url}]}
    livetv = xbmc.getCondVisibility("VideoPlayer.Content(livetv)")
    if not xbmc.getCondVisibility("Player.Paused()"):
        player.pause()
    current_time = parse_time(xbmc.getInfoLabel("Player.Time(hh:mm:ss)"))
    debug("current_time: " + str(current_time))
    cast.media_controller.play_media(url,
                                     content_type,
                                     current_time=current_time,
                                     metadata=metadata)
    progress_dialog.close()
    window_title = "Casting " + title

    debug("livetv: " + str(livetv))
    show_seekbar = not livetv
    total_time = parse_time(xbmc.getInfoLabel("Player.Duration(hh:mm:ss)"))
    debug("total_time: " + str(total_time))
    if total_time:
        percentage = current_time / total_time * 100
    else:
        percentage = 0
    cast_controls_dialog = CastControlsDialog(
        title=window_title,
        cast=cast,
        thumb=thumb,
        show_seekbar=show_seekbar,
        percentage=percentage
    )
    cast_controls_dialog.doModal()
    try:
        cast.media_controller.stop()
    except Exception, e:
        log_exception("Couldn't stop casting")
        log_exception(str(e))


def transform_url(url, show_warnings=True):
    """
    Convert url to supported by Chromecast format
    :param url: original url
    :type url: str
    :param show_warnings: if set True, if url isn't transformed
        error messages and warnings will be shown
    :param show_warnings: bool
    :return: converted url
    :rtype: str or None (if url is't supported by Chromecast)
    """

    if url[:4] == "http":
        return url
    elif url[:4] == "rtmp":
        if show_warnings:
            error("RTMP videos aren't supported")
        return None
    else:
        return transform_local_url(url, show_warnings)


def transform_local_url(url, show_warnings=True):
    """
    Convert local url to url to Kodi web-interface:
    http://<your ip>:<configured port>/vfs/<url encoded vfs path>
    :param url: original url
    :type url: str
    :param show_warnings: in case of any issues (web server isn't enabled,
        couldn't obtain local ip address
    :type show_warnings: bool
    :return: transformed url to Kodi web-interface
    :rtype: str
    """

    if not get_setting("services.webserver"):
        if show_warnings:
            question = xbmcgui.Dialog()
            if question.yesno(
                    "Kastodi",
                    "Casting local videos requires enabling Web server.",
                    "Would you like to turn on Web server now?"
                ):
                if not set_setting_value("services.webserver", True):
                    return None
            else:
                return None
        else:
            return None

    local_ip = get_local_ip()
    if local_ip:
        webserver_port = get_setting("services.webserverport")
        encoded_url = urllib.quote(url)
        new_url = "http://{0}:{1}/vfs/{2}".format(local_ip,
                                                  webserver_port,
                                                  encoded_url)
        return new_url
    else:
        if show_warnings:
            error("Couldn't obtain local ip address")
        return None


def get_setting(name):
    """
    Get Kodi setting
    :param name: id of the setting.
        Example:
    :type name: str
    :return: string value of the setting
    :rtype: str
    """

    command = '{"jsonrpc":"2.0", "id":1, ' \
              '"method":"Settings.GetSettingValue",' \
              '"params":{"setting":"' + name + '"}}'
    try:
        response = xbmc.executeJSONRPC(command)
    except Exception, e:
        log_exception("Couldn't execute JSON-RPC")
        debug(command)
        log_exception(str(e))
        return
    try:
        data = json.loads(response)
    except Exception, e:
        log_exception("Couldn't parse JSON response")
        debug(response)
        log_exception(str(e))
        return None

    debug("data: " + str(data))
    result = data.get("result")
    if result:
        return result.get("value")
    else:
        return None


def set_setting_value(name, value):
    """
    Set Kodi settings value
    :param name: of the setting. Example: "services.webserver"
    :type name: str
    :param value: value of the setting. Example: True
    :return: True - if setting was changed successfully; False - otherwise.
    :rtype: bool
    """

    str_value = json.dumps(value)
    command = '{"jsonrpc":"2.0", "id":1, ' \
              '"method":"Settings.SetSettingValue",' \
              '"params":{"setting":"' + name + '",' \
              '"value":' + str_value + '}}'
    try:
        xbmc.executeJSONRPC(command)
    except Exception, e:
        log_exception("Couldn't change setting")
        debug(command)
        log_exception(str(e))
        return False
    return True


def get_local_ip():
    """
    Get local ip address of the localhost.
    Example: "10.0.0.2"
    :return: local ip address
    :rtype: str
    """

    ranges = ["10.", "172.", "192."]
    all_addresses = zeroconf.get_all_addresses(netifaces.AF_INET)
    for address in all_addresses:
        for ran in ranges:
            if address.startswith(ran):
                return address
    return None


def start_service():
    """
    Start service
    :return: None
    """

    enable_service = this_addon.getSetting("enable_service")
    if enable_service != "true":
        return

    result = add_cast_button()

    if result and NEED_RESTART:
        question = xbmcgui.Dialog()
        if question.yesno("Need restart",
                       "To start casting, you need to restart Kodi. Exit now?"):
            xbmc.executebuiltin("Quit()")

    monitor = xbmc.Monitor()

    while not monitor.abortRequested():
        if monitor.waitForAbort(IDLE_TIME):
            # Abort was requested while waiting. We should exit
            break

    delete_cast_icon()


def add_cast_button():
    """
    Add cast button to Video OSD Window of current skin
    :return: True - if button was added successfully, False - otherwise
    :rtype: bool
    """

    global NEED_RESTART
    current_skin_id = xbmc.getSkinDir()
    skin_folder_home = xbmc.translatePath("special://home/addons/" + current_skin_id)
    if not os.path.exists(skin_folder_home):
        #skin_folder_system = xbmc.translatePath("special://xbmc/addons/" + current_skin)
        current_skin = xbmcaddon.Addon(current_skin_id)
        skin_folder_system = xbmc.translatePath(current_skin.getAddonInfo("path"))
        if not os.path.exists(skin_folder_system):
            error("Couldn't find folder of skin " + current_skin_id)
            return False
        else:
            try:
                shutil.copytree(skin_folder_system, skin_folder_home)
            except Exception, e:
                log_exception(str(e))
                message = "Couldn't copy skin from {0} to {1}".format(skin_folder_system,
                                                                      skin_folder_home)
                error(message)
                return False
            NEED_RESTART = True
    if not copy_icons(skin_folder_home):
        return False
    res_folder = get_default_resolution_folder(skin_folder_home)
    if not res_folder:
        error("Couldn't get default resolution folder for skin " + current_skin_id)
        return False
    videoosdxml_path = os.path.join(skin_folder_home, res_folder, "VideoOSD.xml")
    try:
        with open(videoosdxml_path, "rb") as videoosdxml:
            old_text = videoosdxml.read()
    except Exception, e:
        log_exception("Couldn't get text of VideoOSD.xml")
        log_exception(str(e))
        return
    if old_text.find(CAST_BUTTON_START_TEXT) >= 0:
        NEED_RESTART = False
        return True
    cast_button_text = get_cast_button_text()
    new_text = old_text.replace("</controls>", cast_button_text + "</controls>")
    try:
        with open(videoosdxml_path, "wb") as videoosdxml:
            videoosdxml.write(new_text)
    except Exception, e:
        error("Couldn't write to skin folder")
        log_exception(str(e))
        return False
    if not NEED_RESTART:
        xbmc.executebuiltin("ReloadSkin()")
    return True


def delete_cast_icon():
    """
    Delete Cast icon from current skin
    :return: None
    """

    current_skin_id = xbmc.getSkinDir()
    skin_folder = xbmc.translatePath("special://home/addons/" + current_skin_id)
    res_folder = get_default_resolution_folder(skin_folder)
    if not res_folder:
        log_exception("Couldn't get default resolution folder for skin " + current_skin_id)
        return
    videoosdxml_path = os.path.join(skin_folder, res_folder, "VideoOSD.xml")
    with open(videoosdxml_path, "rb") as videoosdxml:
        old_text = videoosdxml.read()
    start_pos = old_text.find(CAST_BUTTON_START_TEXT)
    if start_pos == -1:
        log_exception("Couldn't find cast button")
        return
    end_pos = old_text.find(CAST_BUTTON_END_TEXT)
    if end_pos == -1:
        log_exception("Couldn't find end of cast button")
        return
    len_end_text = len(CAST_BUTTON_END_TEXT)
    new_text = old_text[:start_pos] + old_text[end_pos + len_end_text:]
    try:
        with open(videoosdxml_path, "wb") as videoosdxml:
            videoosdxml.write(new_text)
    except Exception, e:
        log_exception("Couldn't write to skin VideoOSD.xml")
        log_exception(str(e))


def copy_icons(skin_folder):
    """
    Copy icons from kastodi folder to the folder of current skin
    :param skin_folder: path to current skin folder
    :type skin_folder: str
    :return: True - if icons were successfully copied, False - otherwise
    :rtype: bool
    """

    for icon in ["ic_cast_blue_24dp.png", "ic_cast_white_24dp.png"]:
        try:
            src = image(icon)
            dst = os.path.join(skin_folder, "media", icon)
            shutil.copyfile(src, dst)
        except Exception, e:
            log_exception(str(e))
            message = "Couldn't copy icon from {0} to {1}".format(src, dst)
            error(message)
            return False
    return True


def get_default_resolution_folder(skin_folder):
    """
    Get default resolution folder for current skin
    :return: short name of the folder, example "720p"
    :rtype: str
    """

    addonxmlname = os.path.join(skin_folder, "addon.xml")
    try:
        tree = ET.parse(addonxmlname)
    except Exception, e:
        log_exception("Couldn't parse " + addonxmlname)
        log_exception(str(e))
        return None
    root = tree.getroot()
    aspect_ratio = xbmc.getInfoLabel("Skin.AspectRatio()")
    default = None
    for child in root:
        if child.tag == "extension":
            if child.attrib.get("point", "") == "xbmc.gui.skin":
                for child2 in child:
                    if child2.tag == "res":
                        if child2.attrib.get("aspect","") == aspect_ratio:
                            return child2.attrib.get("folder", None)
                        if child2.attrib.get("default", "") == "true":
                            default = child2.attrib.get("folder", None)
    return default


def get_cast_button_text():
    path = os.path.join(addon_path, "resources", "skin", "CastButton.txt")
    text = ""
    with open(path, "r") as cast_button_template:
        text = cast_button_template.read()
    return text


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


def parse_time(hhmmss):
    """
    Convert time from string hh:mm:ss to number of seconds
    :param hhmmss: string representation of time. Example: "01:15:43"
    :param hhmmss: str
    :return: number of seconds
    :type: float
    """

    time_tuple = hhmmss.split(":")
    num_seconds = float(time_tuple[0]) * 3600
    num_seconds += float(time_tuple[1]) * 60
    num_seconds += float(time_tuple[2])
    return num_seconds

def get_playing_title():
    """
    Get title of currently playing media
    :return: title of media, example: "My Awesome Video"
    :rtype: str
    """

    title = xbmc.getInfoLabel("Player.Title")
    return unicode(title, encoding="utf-8")