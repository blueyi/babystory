
# Copyright (C) 2013 LiuLang <gsushzhsosgsu@gmail.com>

# Use of this source code is governed by GPLv3 license that can be found
# in http://www.gnu.org/licenses/gpl-3.0.html

from gi.repository import GdkPixbuf
from gi.repository import Gtk
import json
import random

from babystory import Config
from babystory import Net
from babystory import Utils
from babystory import Widgets

def song_row_to_dict(song_row, start=0):
    song = {
            'Title': song_row[start],
            'Size': song_row[start+1],
            'Duration': song_row[start+2],
            'Url': song_row[start+3],
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
        left_iconview = Gtk.IconView(model=self.left_liststore)
        left_iconview.set_pixbuf_column(0)
        left_iconview.set_text_column(2)
        left_iconview.props.item_width = 130
        #left_iconview.props.activate_on_single_click = True
        left_iconview.connect('item-activated',
                self.on_left_iconview_item_activated)
        left_window.add(left_iconview)

        self.right_window = Gtk.ScrolledWindow()
        paned.add2(self.right_window)
        paned.child_set_property(self.right_window, 'resize', True)

        # title, size, duration, url
        self.right_liststore = Gtk.ListStore(str, str, str, str)
        self.right_treeview = Gtk.TreeView(model=self.right_liststore)
        self.right_treeview.props.headers_visible = False
        self.right_window.add(self.right_treeview)
        self.right_treeview.connect('row_activated',
                self.on_right_treeview_row_activated)

        title_cell = Gtk.CellRendererText()
        title_col = Widgets.ExpandedTreeViewColumn('Title', title_cell,
                text=0)
        self.right_treeview.append_column(title_col)

        size_cell = Gtk.CellRendererText()
        size_col = Gtk.TreeViewColumn('Size', size_cell, text=1)
        self.right_treeview.append_column(size_col)

        duration_cell = Gtk.CellRendererText()
        duration_col = Gtk.TreeViewColumn('Duration', duration_cell, text=2)
        self.right_treeview.append_column(duration_col)

    def after_init(self):
        self.playlist = Config.load_playlist()
        self.left_liststore.append([self.app.theme['default-icon'], -1,
            'All Categories'])
        for cat_id in self.playlist:
            self.show_category(cat_id)

    def do_destroy(self):
        Config.dump_playlist(self.playlist)

    def on_left_iconview_item_activated(self, iconview, path):
        model = iconview.get_model()
        pix, cat_id, title = model[path]
        self.curr_category = {'Pix': pix, 'Id': cat_id, 'Title': title, }
        self.right_liststore.clear()
        self.right_window.get_vadjustment().set_value(0)

        if cat_id != -1:
            self.append_to_song_liststore(cat_id)
            return
        for cat_id in self.playlist:
            self.append_to_song_liststore(cat_id)

    def on_right_treeview_row_activated(self, treeview, path, column):
        self.curr_playing = int(str(path))
        self.play_song()

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
        self.playlist.remove(cat_id)
        # TODO:

    def append_to_song_liststore(self, cat_id):
        songs_wrap = Net.get_songs(cat_id)
        if songs_wrap is None:
            return
        songs = songs_wrap['Items']
        for song in songs:
            self.right_liststore.append([song['Title'],
                Utils.print_size(song['Size']),
                Utils.print_duration(song['Duration']),
                song['Url'], ])

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
        print(self.curr_playing, self.prev_playing, self.next_playing)
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
        song['category'] = self.curr_category
        return song
