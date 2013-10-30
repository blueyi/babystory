
# Copyright (C) 2013 LiuLang <gsushzhsosgsu@gmail.com>

# Use of this source code is governed by GPLv3 license that can be found
# in http://www.gnu.org/licenses/gpl-3.0.html

from gi.repository import GdkPixbuf
from gi.repository import Gdk
from gi.repository import Gtk
import json
import random

from babystory.Cache import Cache
from babystory import Config
from babystory import Net
from babystory import Utils
from babystory import Widgets

_ = Config._
TITLE, SIZE, DURATION, URL, CATEGORY = list(range(5))


def song_row_to_dict(song_row):
    song = {
            'Title': song_row[TITLE],
            'Size': song_row[SIZE],
            'Duration': song_row[DURATION],
            'Url': song_row[URL],
            'Category': song_row[CATEGORY],
            }
    return song

class Playlist(Gtk.Box):
    def __init__(self, app):
        self.app = app
        super().__init__()

        self.curr_playing = None
        self.prev_playing = None
        self.next_playing = None

        self.control_box = Gtk.Box()
        self.pack_start(self.control_box, False, False, 0)
        
        paned = Gtk.Paned()
        self.pack_start(paned, True, True, 0)

        left_window = Gtk.ScrolledWindow()
        paned.add1(left_window)
        paned.child_set_property(left_window, 'resize', True)

        # icon, id, title, 
        self.left_liststore = Gtk.ListStore(GdkPixbuf.Pixbuf, int, str)
        self.left_iconview = Gtk.IconView(model=self.left_liststore)
        self.left_iconview.set_pixbuf_column(0)
        self.left_iconview.set_text_column(2)
        self.left_iconview.props.item_width = 130
        if Gtk.MINOR_VERSION > 6:
            self.left_iconview.props.activate_on_single_click = True
        self.left_iconview.connect('button-press-event',
                self.on_left_iconview_button_pressed)
        left_window.add(self.left_iconview)

        self.left_menu = Gtk.Menu()
        self.left_menu_cache = Gtk.MenuItem(_('Cache'))
        self.left_menu_cache.connect('activate',
                self.on_left_menu_cache_activated)
        self.left_menu.append(self.left_menu_cache)
        sep = Gtk.SeparatorMenuItem()
        self.left_menu.append(sep)
        self.left_menu_delete = Gtk.MenuItem(_('Delete'))
        self.left_menu_delete.connect('activate',
                self.on_left_menu_delete_activated)
        self.left_menu.append(self.left_menu_delete)

        self.right_window = Gtk.ScrolledWindow()
        paned.add2(self.right_window)
        paned.child_set_property(self.right_window, 'resize', True)

        # title, size, duration, url, category
        self.right_liststore = Gtk.ListStore(str, str, str, str, str)
        self.right_treeview = Gtk.TreeView(model=self.right_liststore)
        self.right_treeview.props.headers_visible = False
        self.right_window.add(self.right_treeview)
        self.right_treeview.connect('row_activated',
                self.on_right_treeview_row_activated)

        title_cell = Gtk.CellRendererText()
        title_col = Widgets.ExpandedTreeViewColumn(_('Title'), title_cell,
                text=TITLE)
        self.right_treeview.append_column(title_col)

        size_cell = Gtk.CellRendererText()
        size_col = Gtk.TreeViewColumn(_('Size'), size_cell, text=SIZE)
        self.right_treeview.append_column(size_col)

        duration_cell = Gtk.CellRendererText()
        duration_col = Gtk.TreeViewColumn(_('Duration'), duration_cell,
                text=DURATION)
        self.right_treeview.append_column(duration_col)

    def after_init(self):
        self.playlist = Config.load_playlist()
        self.left_liststore.append([self.app.theme['default-icon'], -1,
            'All Categories'])
        for cat_id in self.playlist:
            self.show_category(cat_id)

    # signal handlers starts
    def do_destroy(self):
        Config.dump_playlist(self.playlist)

    def on_left_iconview_button_pressed(self, iconview, event):
        if event.type != Gdk.EventType.BUTTON_PRESS:
            return False
        path = iconview.get_path_at_pos(event.x, event.y)
        if path is None:
            iconview.unselect_all()

        if event.button == Gdk.BUTTON_PRIMARY:
            if path is not None:
                self.on_left_iconview_item_activated(iconview, path)
            return True
        elif event.button == Gdk.BUTTON_SECONDARY:
            self.on_left_iconview_popup_menu(iconview, path, event)
            return True
        return False

    def on_left_iconview_popup_menu(self, iconview, path, event):
        self.left_menu.path = path
        if path is not None:
            self.on_left_iconview_item_activated(iconview, path)
            self.left_menu_delete.set_label(_('Delete'))
            self.left_menu_cache.set_label(_('Cache'))
        else:
            self.left_menu_delete.set_label(_('Delete All'))
            self.left_menu_cache.set_label(_('Cache All'))
        self.left_menu.show_all()
        self.left_menu.popup(None, None, None, None,
                event.button, event.time)

    def on_left_iconview_item_activated(self, iconview, path):
        self.left_iconview.select_path(path)
        model = self.left_iconview.get_model()
        pix, cat_id, title = model[path]
        self.curr_category = {'Pix': pix, 'Id': cat_id, 'Title': title, }
        self.right_liststore.clear()
        self.right_window.get_vadjustment().set_value(0)

        if cat_id != -1:
            self.append_song_to_liststore(cat_id)
            return
        for cat_id in self.playlist:
            self.append_song_to_liststore(cat_id)

    def on_left_menu_delete_activated(self, menu_item):
        path = self.left_menu.path
        if path is None or int(str(path)) == 0:
            while len(self.playlist) > 0:
                cat_id = self.playlist[len(self.playlist) - 1]
                self.remove_category(cat_id)
            return
        icon, cat_id, title = self.left_liststore[path]
        self.remove_category(cat_id)

    def on_left_menu_cache_activated(self, menu_item):
        path = self.left_menu.path
        if path is None:
            _path = Gtk.TreePath(0)
            self.left_iconview.select_path(_path)
            self.on_left_iconview_item_activated(self.left_iconview, _path)
        self.cache_job = Cache(self.app)
        self.cache_job.run()
        self.cache_job.destroy()

    def on_right_treeview_row_activated(self, treeview, path, column):
        self.play_song_at(int(str(path)))
    # signal handlers ends

    # 
    def show_category(self, cat_id):
        category = self.app.categories.category_list[str(cat_id)]
        image_path = Net.get_image(category['IconUrl'])
        if image_path:
            pix = GdkPixbuf.Pixbuf.new_from_file(image_path)
        else:
            pix = self.app.theme['default-icon']
        self.left_liststore.append([pix, category['Id'], category['Title']])

    def append_category(self, cat_id):
        if cat_id in self.playlist:
            return
        self.playlist.append(cat_id)
        self.show_category(cat_id)

    def remove_category(self, cat_id):
        if cat_id == -1:
            return
        index = self.playlist.index(cat_id)
        path = Gtk.TreePath(index + 1)
        _iter = self.left_liststore.get_iter(path)
        self.left_liststore.remove(_iter)
        self.playlist.remove(cat_id)

    def append_song_to_liststore(self, cat_id):
        songs_wrap = Net.get_songs(cat_id)
        if songs_wrap is None:
            return
        songs = songs_wrap['Items']
        category = self.get_category_title(cat_id)
        print('category:', category)
        for song in songs:
            self.right_liststore.append([
                song['Title'],
                Utils.print_size(song['Size']),
                Utils.print_duration(song['Duration']),
                song['Url'],
                category,
                ])

    def get_prev_song(self, repeat=False, shuffle=False):
        song_nums = len(self.right_liststore)
        if song_nums == 0:
            return None
        path = self.curr_playing
        if path == 0:
            if repeat:
                path = song_nums - 1
            else:
                path = 0
        else:
            path = path - 1
        self.prev_playing = path
        return self.get_song_from_index(self.prev_playing)

    def get_next_song(self, repeat=False, shuffle=False):
        song_nums = len(self.right_liststore)
        if song_nums == 0:
            return None
        path = self.curr_playing
        if shuffle:
            path = random.randint(0, song_nums-1)
        elif path == song_nums - 1:
            if repeat is False:
                self.next_playing = None
                return None
            path = 0
        else:
            path = path + 1
        self.next_playing = path
        return self.get_song_from_index(self.next_playing)

    def play_prev_song(self, repeat=False, shuffle=False):
        if self.prev_playing is None:
            song = self.get_prev_song(repeat=repeat, shuffle=shuffle)
            if song is None:
                return
        self.curr_playing = self.prev_playing
        self.prev_playing = None
        self.play_song()

    def play_song(self):
        selection = self.right_treeview.get_selection()
        path = Gtk.TreePath(self.curr_playing)
        selection.select_path(path)
        song = self.get_song_from_index(self.curr_playing)
        self.app.player.load(song)

    def play_song_at(self, pos):
        print('play song at:', pos)
        self.curr_playing = pos
        self.play_song()

    def play_next_song(self, repeat=False, shuffle=False):
        if self.next_playing is None:
            song = self.get_next_song(repeat=repeat, shuffle=shuffle)
            if song is None:
                return
        self.curr_playing = self.next_playing
        self.next_playing = None
        self.play_song()

    def get_song_from_index(self, index):
        row = self.right_liststore[index]
        song = song_row_to_dict(row)
        return song

    def get_category_title(self, cat_id):
        return self.app.categories.category_list[str(cat_id)]['Title']

    def activate_iconview_item_with_cat_id(self, cat_id):
        i = 0
        for cate in self.left_liststore:
            if cate[1] == cat_id:
                break
            i += 1
        path = Gtk.TreePath(i)
        self.on_left_iconview_item_activated(self.left_iconview, path)
