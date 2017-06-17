# !/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import sublime
import sublime_plugin
import threading

from os import path

from .commands import *
from .beginning.pio_install import PioInstall
from .platformio.project_recognition import ProjectRecognition
from .platformio.compile import Compile
from .platformio.upload import Upload
from .platformio.clean import Clean
from .libraries.quick_menu import QuickMenu
from .libraries.tools import get_setting, save_setting, create_sketch, select_dir, add_library_to_sketch
from .platformio.initialize import Initialize
from .libraries.libraries import Libraries
from .libraries.paths import getBoardsFileDataPath, getMainMenuPath
from .platformio.pio_bridge import PioBridge

from time import sleep

def plugin_loaded():
    PioInstall()

    boards_file = getBoardsFileDataPath()

    if(not path.exists(boards_file)):
        PioBridge().save_boards_list()

    menu_path = getMainMenuPath()
    compile_lang = get_setting('compile_lang', True)
    
    if(compile_lang or not path.exists(menu_path)):
        from .libraries.top_menu import TopMenu
        TopMenu().create_main_menu()
        save_setting('compile_lang', False)



class DeviotListener(sublime_plugin.EventListener):
    def on_activated(self, view):
        #
        pass
    
    def on_close(self, view):
        from .libraries import serial
        if(serial.serials_in_use):
            for port_id in serial.serials_in_use:
                serial_monitor = serial.serial_monitor_dict.get(port_id, None)
                serial_monitor.stop()
                serial.serials_in_use.remove(port_id)
                del serial.serial_monitor_dict[port_id]

class DeviotNewSketch(sublime_plugin.WindowCommand):
    def run(self):
        from .libraries.I18n import I18n
        caption = I18n().translate('caption_new_sketch')
        self.window.show_input_panel(caption, '', self.on_done, None, None)

    def on_done(self, sketch_name):
        select_dir(self.window, key=sketch_name, func=create_sketch)

class DeviotSaveBoards(sublime_plugin.WindowCommand):
    def run(self):
        PioBridge().save_boards_list()

class DeviotTestCommand(sublime_plugin.WindowCommand):
    def run(self):
        Initialize()
        # TopMenu()
        pass
class DeviotSelectBoardsCommand(sublime_plugin.WindowCommand):
    def run(self):
        QuickMenu().quick_boards()

class DeviotSelectEnvironmentCommand(sublime_plugin.WindowCommand):
    def run(self):
        QuickMenu().quick_environments()

class DeviotCompileSketchCommand(sublime_plugin.WindowCommand):
    def run(self):
        Compile()

class DeviotUploadSketchCommand(sublime_plugin.WindowCommand):
    def run(self):
        Upload()

class DeviotCleanSketchCommand(sublime_plugin.WindowCommand):
    def run(self):
        Clean()

class DeviotOpenIniFile(sublime_plugin.WindowCommand):

    def run(self):
        views = []

        ini_file = ProjectRecognition().get_ini_path()
        view = self.window.open_file(ini_file)
        views.append(view)

        if views:
            self.window.focus_view(views[0])

    def is_enabled(self):
        from .libraries.project_check import ProjectCheck
        check = ProjectCheck()
        return check.is_iot()


class DeviotSelectPortCommand(sublime_plugin.WindowCommand):
    def run(self):
        QuickMenu().quick_serial_ports()

class DeviotLanguagesCommand(sublime_plugin.WindowCommand):
    def run(self):
        QuickMenu().quick_language()

class HideConsoleCommand(sublime_plugin.WindowCommand):
    """
    Hide the deviot console

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        self.window.run_command("hide_panel", {"panel": "output.exec"})


class ShowConsoleCommand(sublime_plugin.WindowCommand):
    """
    Hide the deviot console

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        self.window.run_command("show_panel", {"panel": "output.exec"})