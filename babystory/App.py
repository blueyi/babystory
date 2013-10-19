
# Copyright (C) 2013 LiuLang <gsushzhsosgsu@gmail.com>

# Use of this source code is governed by GPLv3 license that can be found
# in http://www.gnu.org/licenses/gpl-3.0.html

from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import GObject
from gi.repository import Gtk
import os
import sys

from babystory import Config
Config.check_first()
_ = Config._

from babystory.Categories import Categories
from babystory.Player import Player
from babystory.Playlist import Playlist

GObject.threads_init()

class App:

    def __init__(self):
        self.app = Gtk.Application.new('org.liulang.babystory', 0)
        self.app.connect('startup', self.on_app_startup)
        self.app.connect('activate', self.on_app_activate)
        self.app.connect('shutdown', self.on_app_shutdown)

        self.conf = Config.load_conf()
        self.theme = Config.load_theme()

    def on_app_startup(self, app):
        self.window = Gtk.ApplicationWindow(application=app)
        self.window.set_default_size(*self.conf['window-size'])
        self.window.set_title(Config.APPNAME)
        self.window.props.hide_titlebar_when_maximized = True
        self.window.set_icon(self.theme['app-logo'])
        app.add_window(self.window)
        self.window.connect('check-resize',
                self.on_main_window_resized)
        self.window.connect('delete-event',
                self.on_main_window_deleted)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.window.add(box)

        self.player = Player(self)
        box.pack_start(self.player, False, False, 0)

        self.categories = Categories(self)
        box.pack_start(self.categories, True, True, 0)

        self.playlist = Playlist(self)
        box.pack_start(self.playlist, True, True, 0)

    def on_app_activate(self, app):
        self.window.show_all()
        self.categories.after_init()
        self.playlist.hide()
        self.playlist.after_init()
        self.player.after_init()

    def run(self, argv):
        self.app.run(argv)

    def quit(self):
        self.window.destroy()
        self.app.quit()

    def on_app_shutdown(self, app):
        Config.dump_conf(self.conf)

    def on_main_window_resized(self, window, event=None):
        self.conf['window-size'] = window.get_size()

    def on_main_window_deleted(self, window, event):
        return False
