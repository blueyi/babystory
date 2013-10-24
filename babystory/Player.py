
# Copyright (C) 2013 LiuLang <gsushzhsosgsu@gmail.com>

# Use of this source code is governed by GPLv3 license that can be found
# in http://www.gnu.org/licenses/gpl-3.0.html

from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Gtk
import sys
import time

from babystory import Config
from babystory import Net
from babystory.Preferences import Preferences
from babystory.PlayerBin import PlayerBin
from babystory import Utils
from babystory import Widgets

_ = Config._
# Gdk.EventType.2BUTTON_PRESS is an invalid variable
GDK_2BUTTON_PRESS = 5
# set toolbar icon size to Gtk.IconSize.DND
ICON_SIZE = 5

class RepeatType:
    NONE = 0
    ALL = 1
    ONE = 2

class PlayType:
    NONE = 0
    SONG = 1


class Player(Gtk.Toolbar):
    def __init__(self, app):
        self.app = app
        super().__init__()

        self.async_song = None
        self.async_next_song = None
        self.adj_timeout = 0
        self.play_type = PlayType.NONE

        self.set_style(Gtk.ToolbarStyle.ICONS)
        self.get_style_context().add_class(Gtk.STYLE_CLASS_PRIMARY_TOOLBAR)
        self.set_show_arrow(False)
        self.set_icon_size(ICON_SIZE)

        prev_button = Gtk.ToolButton()
        prev_button.set_label(_('Previous'))
        prev_button.set_icon_name('media-skip-backward-symbolic')
        prev_button.connect('clicked', self.on_prev_button_clicked)
        self.insert(prev_button, 0)

        self.play_button = Gtk.ToolButton()
        self.play_button.set_label(_('Play'))
        self.play_button.set_icon_name('media-playback-start-symbolic')
        self.play_button.connect('clicked', self.on_play_button_clicked)
        self.insert(self.play_button, 1)

        next_button = Gtk.ToolButton()
        next_button.set_label(_('Next'))
        next_button.set_icon_name('media-skip-forward-symbolic')
        next_button.connect('clicked', self.on_next_button_clicked)
        self.insert(next_button, 2)

        sep = Gtk.SeparatorToolItem()
        self.insert(sep, 3)

        self.shuffle_btn = Gtk.ToggleToolButton()
        self.shuffle_btn.set_label(_('Shuffle'))
        self.shuffle_btn.set_icon_name('media-playlist-shuffle-symbolic')
        self.insert(self.shuffle_btn, 4)

        self.repeat_type = RepeatType.NONE
        self.repeat_btn = Gtk.ToggleToolButton()
        self.repeat_btn.set_label(_('Repeat'))
        self.repeat_btn.set_icon_name('media-playlist-repeat-symbolic')
        self.repeat_btn.connect('clicked', self.on_repeat_button_clicked)
        self.insert(self.repeat_btn, 5)

        scale_tool_item = Gtk.ToolItem()
        self.insert(scale_tool_item, 6)
        self.child_set_property(scale_tool_item, 'expand', True)
        scale_box = Gtk.Box(spacing=3)
        scale_box.props.margin_left = 5
        scale_tool_item.add(scale_box)

        self.scale = Gtk.Scale()
        self.adjustment = Gtk.Adjustment(0, 0, 100, 1, 10, 0)
        #self.adjustment.connect('changed', self.on_adjustment_changed)
        self.scale.set_adjustment(self.adjustment)
        self.scale.set_restrict_to_fill_level(False)
        self.scale.props.draw_value = False
        self.scale.connect('change-value', self.on_scale_change_value)
        scale_box.pack_start(self.scale, True, True, 0)

        self.time_label = Gtk.Label('0:00/0:00')
        scale_box.pack_start(self.time_label, False, False, 0)

        self.volume = Gtk.VolumeButton()
        self.volume.props.use_symbolic = True
        self.volume.set_value(app.conf['volume'] ** 0.33)
        self.volume.connect('value-changed', self.on_volume_value_changed)
        scale_box.pack_start(self.volume, False, False, 0)

        home_button = Gtk.ToggleToolButton()
        home_button.set_label(_('Home'))
        home_button.set_icon_name('user-home-symbolic')
        home_button.set_active(True)
        home_button.set_tooltip_text('Show playlist or category list')
        home_button.connect('toggled', self.on_home_button_toggled)
        self.insert(home_button, 7)

        # contro menu
        menu_tool_item = Gtk.ToolItem()
        self.insert(menu_tool_item, 8)
        main_menu = Gtk.Menu()
        pref_item = Gtk.MenuItem(label=_('Preferences'))
        pref_item.connect('activate',
                self.on_main_menu_pref_activate)
        main_menu.append(pref_item)
        sep_item = Gtk.SeparatorMenuItem()
        main_menu.append(sep_item)
        about_item = Gtk.MenuItem(label=_('About'))
        about_item.connect('activate',
                self.on_main_menu_about_activate)
        main_menu.append(about_item)
        quit_item = Gtk.MenuItem(label=_('Quit'))
        quit_item.connect('activate', 
                self.on_main_menu_quit_activate)
        main_menu.append(quit_item)
        main_menu.show_all()
        menu_image = Gtk.Image()
        menu_image.set_from_icon_name('view-list-symbolic', ICON_SIZE)
        if Gtk.MINOR_VERSION < 6:
            menu_btn = Gtk.Button()
            menu_btn.connect('clicked', 
                self.on_main_menu_button_clicked, main_menu)
        else:
            menu_btn = Gtk.MenuButton()
            menu_btn.set_popup(main_menu)
            menu_btn.set_always_show_image(True)
        menu_btn.props.halign = Gtk.Align.END
        menu_btn.props.halign = Gtk.Align.END
        menu_btn.set_image(menu_image)
        menu_tool_item.add(menu_btn)

        # init playbin
        self.playbin = PlayerBin()
        self.playbin.connect('eos', self.on_playbin_eos)
        self.playbin.connect('error', self.on_playbin_error)

    def after_init(self):
        pass

    def do_destroy(self):
        print('Player.do_destroy()')
        self.playbin.destroy()
        if self.async_song:
            self.async_song.destroy()
        if self.async_next_song:
            self.async_next_song.destroy()

    # signal handlers for toolbar items
    def on_prev_button_clicked(self, button):
        if self.play_type == PlayType.SONG:
            self.load_prev()

    def on_play_button_clicked(self, button):
        if self.play_type == PlayType.SONG:
            self.play_pause()

    def on_next_button_clicked(self, button):
        if self.play_type == PlayType.SONG:
            self.load_next_cb()

    def on_repeat_button_clicked(self, button):
        if self.repeat_type == RepeatType.NONE:
            self.repeat_type = RepeatType.ALL
            button.set_active(True)
            button.set_icon_name('media-playlist-repeat-symbolic')
        elif self.repeat_type == RepeatType.ALL:
            self.repeat_type = RepeatType.ONE
            button.set_active(True)
            button.set_icon_name('media-playlist-repeat-song-symbolic')
        elif self.repeat_type == RepeatType.ONE:
            self.repeat_type = RepeatType.NONE
            button.set_active(False)
            button.set_icon_name('media-playlist-repeat-symbolic')

    def on_scale_change_value(self, scale, scroll_type, value):
        self.seek(value)

    def on_volume_value_changed(self, volume, value):
        self.set_volume(value ** 3)

    def on_home_button_toggled(self, button):
        if button.get_active():
            self.app.playlist.hide()
            self.app.categories.show()
        else:
            self.app.categories.hide()
            self.app.playlist.show_all()

    # menu button
    def on_main_menu_button_clicked(self, button, main_menu):
        main_menu.popup(None, None, None, None, 1, 
            Gtk.get_current_event_time())

    def on_main_menu_pref_activate(self, menu_item):
        dialog = Preferences(self.app)
        dialog.run()
        dialog.destroy()

    def on_main_menu_about_activate(self, menu_item):
        dialog = Gtk.AboutDialog()
        dialog.set_modal(True)
        dialog.set_transient_for(self.app.window)
        dialog.set_program_name(Config.APPNAME)
        dialog.set_logo(self.app.theme['app-logo'])
        dialog.set_version(Config.VERSION)
        dialog.set_comments(Config.DESCRIPTION)
        dialog.set_copyright(Config.COPYRIGHT)
        dialog.set_website(Config.HOMEPAGE)
        dialog.set_license_type(Gtk.License.GPL_3_0)
        dialog.set_authors(Config.AUTHORS)
        dialog.run()
        dialog.destroy()

    def on_main_menu_quit_activate(self, menu_item):
        self.app.quit()

    # playbin signal handlers
    def on_playbin_eos(self, *args):
        self.load_next_cb()

    def on_playbin_error(self, widget, error_msg):
        self.load_next_cb()


    # player wrapper
    def play_pause(self):
        if self.playbin.is_playing():
            self.pause_player()
        else:
            self.start_player()

    def start_player(self, load=False):
        self.play_button.set_icon_name('media-playback-pause-symbolic')
        self.playbin.play()
        self.adj_timeout = GLib.timeout_add(250, self.sync_adjustment)
        if load:
            GLib.timeout_add(1500, self.init_adjustment)

    def pause_player(self):
        self.play_button.set_icon_name('media-playback-start-symbolic')
        self.playbin.pause()
        if self.adj_timeout > 0:
            GLib.source_remove(self.adj_timeout)
            self.adj_timeout = 0

    def stop_player(self):
        self.play_button.set_icon_name('media-playback-pause-symbolic')
        self.scale.set_sensitive(True)
        self.scale.set_fill_level(0)
        self.scale.set_show_fill_level(False)
        self.playbin.stop()
        self.scale.set_value(0)
        self.scale.set_sensitive(False)
        self.time_label.set_label('0:00/0:00')
        if self.adj_timeout > 0:
            GLib.source_remove(self.adj_timeout)
            self.adj_timeout = 0

    def load_prev(self):
        self.stop_player()
        _repeat = self.repeat_btn.get_active()
        _shuffle = self.shuffle_btn.get_active()
        self.app.playlist.play_prev_song(repeat=_repeat, shuffle=_shuffle)

    def load(self, song):
        self.play_type = PlayType.SONG
        self.curr_song = song
        self.update_window_title()
        self.stop_player()
        self.scale.set_sensitive(False)
        self.scale.set_fill_level(0)
        self.scale.set_show_fill_level(True)
        self.async_song = Net.AsyncSong(self.app)
        self.async_song.connect('chunk-received', self.on_chunk_received)
        self.async_song.connect('can-play', self.on_song_can_play)
        self.async_song.connect('downloaded', self.on_song_downloaded)
        self.async_song.get_song(song)

    def load_next(self):
        if self.play_type == PlayType.NONE:
            return
        self.stop_player()
        if self.repeat_type == RepeatType.ONE:
            self.load(self.curr_song)
            return
        if self.next_song is None:
            return
        _repeat = self.repeat_btn.get_active()
        _shuffle = self.shuffle_btn.get_active()
        self.app.playlist.play_next_song(repeat=_repeat, shuffle=_shuffle)

    def load_next_cb(self):
        GLib.idle_add(self.load_next)

    def seek(self, offset):
        if self.play_type == PlayType.NONE:
            return
        self.playbin.seek(offset)
        self.sync_label_by_adjustment()

    def set_volume(self, volume):
        self.app.conf['volume'] = volume
        self.playbin.set_volume(volume)

    def failed_to_download(self, song_path, status):
        print('Player.failed_to_download()')
        self.pause_player()
        
        if status == 'FileNotFoundError':
            Widgets.filesystem_error(self.app.window, song_path)
        elif status == 'URLError':
            msg = _('Failed to download song')
            Widgets.network_error(self.app.window, msg)

    def on_chunk_received(self, widget, percent):
        def _update_fill_level():
            self.scale.set_fill_level(percent)
        GLib.idle_add(_update_fill_level)

    def on_song_can_play(self, widget, song_path, status):
        def _on_song_can_play():
            self.scale.set_show_fill_level(False)
            self.scale.set_fill_level(0)

            uri = 'file://' + song_path
            self.meta_url = uri
            self.playbin.load_audio(uri)
            self.start_player(load=True)

        def _load_next():
            self.load_next_cb()

        if status == 'OK':
            GLib.idle_add(_on_song_can_play)
        elif status in ('URLError', 'FileNotFoundError'):
            GLib.idle_add(self.failed_to_download, song_path, status)

    def on_song_downloaded(self, widget, song_path):
        def _on_song_download():
            self.scale.set_sensitive(True)
            self.init_adjustment()
            _repeat = self.repeat_btn.get_active()
            _shuffle = self.shuffle_btn.get_active()
            self.next_song = self.app.playlist.get_next_song(
                    shuffle=_shuffle, repeat=_repeat)
            if self.next_song:
                self.cache_next_song()

        if song_path:
            GLib.idle_add(_on_song_download)
        else:
            #GLib.idle_add(self.failed_to_download, song_path)
            self.load_next_cb()
            pass

    def cache_next_song(self):
        self.async_next_song = Net.AsyncSong(self.app)
        self.async_next_song.get_song(self.next_song)

    def init_adjustment(self):
        self.adjustment.set_value(0.0)
        self.adjustment.set_lower(0.0)
        status, duration = self.playbin.get_duration()
        if status and duration > 0:
            self.adjustment.set_upper(duration)
            return False
        return True

    def sync_adjustment(self):
        status, offset = self.playbin.get_position()
        if not status:
            return True

        status, duration = self.playbin.get_duration()
        self.adjustment.set_value(offset)
        self.adjustment.set_upper(duration)
        self.sync_label_by_adjustment()
        if offset >= duration - 800000000:
            self.load_next_cb()
            return False
        return True

    def sync_label_by_adjustment(self):
        curr = Utils.print_nano_duration(self.adjustment.get_value())
        total = Utils.print_nano_duration(self.adjustment.get_upper())
        self.time_label.set_label('{0}/{1}'.format(curr, total))

    def update_window_title(self):
        self.app.window.set_title('{0} - {1}'.format(
            self.curr_song['Title'], self.curr_song['Category']))
