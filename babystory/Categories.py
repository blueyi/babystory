
# Copyright (C) 2013 LiuLang <gsushzhsosgsu@gmail.com>

# Use of this source code is governed by GPLv3 license that can be found
# in http://www.gnu.org/licenses/gpl-3.0.html

from gi.repository import GdkPixbuf
from gi.repository import GLib
from gi.repository import Gtk

from babystory import Config
from babystory import Net
from babystory import Utils
from babystory import Widgets


class CatButton(Gtk.Button):
    def __init__(self, categories):
        self.categories = categories
        label = categories.right_label.get_text()
        super().__init__(label)
        self.set_relief(Gtk.ReliefStyle.NONE)
        self.connect('clicked', self.on_button_clicked)

    def on_button_clicked(self, btn):
        self.categories.add_button.hide()
        notebook = self.categories.notebook
        cat_tabs = notebook.get_children()[1:]
        button_box = self.categories.cat_control_box
        cat_buttons = button_box.get_children()
        index = cat_buttons.index(self)

        self.categories.popup(cat_tabs[index])
        for tab in cat_tabs[index+2:]:
            notebook.remove(tab)

        self.categories.right_label.set_text(cat_buttons[index].get_label())
        for button in cat_buttons[index:]:
            button_box.remove(button)

class CatIconTab(Gtk.ScrolledWindow):
    def __init__(self, categories, cat_id):
        super().__init__()
        self.categories = categories
        self.cat_id = cat_id
        # icon, cat_id, title, hasChild
        self.liststore = Gtk.ListStore(GdkPixbuf.Pixbuf, int, str, bool)
        iconview = Gtk.IconView(model=self.liststore)
        iconview.set_pixbuf_column(0)
        iconview.set_text_column(2)
        iconview.props.item_width = 130
        iconview.props.activate_on_single_click = True
        iconview.connect('item-activated', self.on_iconview_item_activated)
        self.add(iconview)

        if len(categories.category_list[str(cat_id)]['Children']) > 0:
            self.insert_items()
        else:
            self.get_items()

    def insert_items(self):
        children = self.categories.category_list[str(self.cat_id)]['Children']
        i = 0
        for cat_id in children:
            item = self.categories.category_list[str(cat_id)]
            self.liststore.append([self.categories.default_icon,
                cat_id, item['Title'], item['HasChild'], ])
            Net.update_liststore_image(self.liststore, i, 0,
                    item['IconUrl'])
            i += 1
        self.show_all()

    def get_items(self):
        def _get_items(category_list, error=None):
            if category_list is None:
                print('Failed to get category list')
                return
            lists = self.categories.category_list
            curr_list = self.categories.category_list[str(self.cat_id)]
            for item in category_list['Items']:
                curr_list['Children'].append(item['Id'])
                lists[str(item['Id'])] = {
                        'Id': item['Id'],
                        'Parent': self.cat_id,
                        'Title': item['Title'],
                        'IconUrl': item['IconUrl'],
                        'HasChild': item['HasChild'],
                        }
                if item['HasChild']:
                    lists[str(item)]['Children'] = []
            GLib.idle_add(self.insert_items)

        Net.async_call(Net.get_categories, _get_items, self.cat_id)

    def on_iconview_item_activated(self, iconview, path):
        model = iconview.get_model()
        cat_id = model[path][1]
        if self.categories.category_list[str(cat_id)]['HasChild']:
            self.categories.append_icon_tab(cat_id)
        else:
            self.categories.show_songs(cat_id)


class CatSongTab(Gtk.ScrolledWindow):
    def __init__(self, categories):
        super().__init__()
        self.categories = categories

        # id, title, format, size, duration, url
        self.liststore = Gtk.ListStore(int, str, str, str, str, str)
        treeview = Gtk.TreeView(model=self.liststore)
        self.add(treeview)
        #treeview.props.headers_visible = False

        title_cell = Gtk.CellRendererText()
        title_col = Widgets.ExpandedTreeViewColumn('Title', title_cell,
                text=1)
        treeview.append_column(title_col)

#        format_cell = Gtk.CellRendererText()
#        format_col = Gtk.TreeViewColumn('Format', format_cell, text=2)
#        treeview.append_column(format_col)

        size_cell = Gtk.CellRendererText()
        size_col = Gtk.TreeViewColumn('Size', size_cell, text=3)
        treeview.append_column(size_col)

        duration_cell = Gtk.CellRendererText()
        duration_col = Gtk.TreeViewColumn('Duration', duration_cell, text=4)
        treeview.append_column(duration_col)

#        url_cell = Gtk.CellRendererText()
#        url_col = Gtk.TreeViewColumn('Url', url_cell, text=5)
#        treeview.append_column(url_col)

    def show_songs(self, cat_id):
        self.liststore.clear()
        songs_wrap = Net.get_songs(cat_id)
        if songs_wrap is None:
            print('Failed to get songs')
            return
        songs = songs_wrap['Items']
        for song in songs:
            self.liststore.append([song['Id'], song['Title'],
                song['Format'], Utils.print_size(song['Size']),
                Utils.print_duration(song['Duration']), song['Url'], ])
        self.show_all()


class Categories(Gtk.Box):
    def __init__(self, app):
        self.app = app
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        control_box = Gtk.Box()
        control_box.props.margin_left = 5
        control_box.props.margin_right = 5
        self.pack_start(control_box, False, False, 0)

        self.cat_control_box = Gtk.Box(spacing=5)
        self.cat_control_box.props.margin_right = 5
        control_box.pack_start(self.cat_control_box, False, False, 0)

        self.right_control_box = Gtk.Box()
        control_box.pack_end(self.right_control_box, True, True, 0)

        self.right_label = Gtk.Label('')
        self.right_label.props.margin_top = 4
        self.right_label.props.margin_bottom = 4
        self.right_label.props.margin_left = 4
        self.right_control_box.pack_start(self.right_label, False, False, 0)

        self.add_button = Gtk.Button('Add to playlist')
        self.add_button.set_relief(Gtk.ReliefStyle.NONE)
        self.add_button.connect('clicked', self.on_add_button_clicked)
        self.right_control_box.pack_end(self.add_button, False, False, 0)

        self.notebook = Gtk.Notebook()
        self.notebook.set_show_tabs(False)
        self.pack_start(self.notebook, True, True, 0)

        self.default_icon = app.theme['default-icon']
        self.category_list = Config.load_category_list()

    def after_init(self):
        self.add_button.hide()
        self.song_tab = CatSongTab(self)
        self.song_tab.page_num = self.notebook.append_page(
                self.song_tab, Gtk.Label('Songs'))

        root_cat_tab = CatIconTab(self, '0')
        root_cat_tab.page_num = self.notebook.append_page(
                root_cat_tab, Gtk.Label('Baby Story'))
        root_cat_tab.show_all()

        self.right_label.set_text('Baby Stroy')

    def append_icon_tab(self, cat_id):
        cat_tab = CatIconTab(self, cat_id)
        cat_title = self.category_list[str(cat_id)]['Title']
        cat_tab.page_num = self.notebook.append_page(
            cat_tab, Gtk.Label(cat_title))
        self.popup(cat_tab)
        self.push_button(cat_id)

    def remove_icon_tab(self):
        pass

    def show_songs(self, cat_id):
        self.add_button.show_all()
        self.push_button(cat_id)
        self.song_tab.show_songs(cat_id)
        self.song_tab.cat_id = cat_id
        self.popup(self.song_tab)

    def push_button(self, cat_id):
        cat_title = self.category_list[str(cat_id)]['Title']
        cat_button = CatButton(self)
        self.cat_control_box.pack_start(cat_button, False, False, 0)
        cat_button.show_all()
        self.right_label.set_text(cat_title)

    def pop_button(self):
        pass

    def popup(self, widget):
        widget.show_all()
        self.notebook.set_current_page(widget.page_num)

    def do_destroy(self):
        #print('category list:', self.category_list)
        Config.dump_category_list(self.category_list)

    def on_add_button_clicked(self, button):
        print('on add button clicked()')
        if len(self.song_tab.liststore) == 0:
            return
        self.app.playlist.append_category(self.song_tab.cat_id)
