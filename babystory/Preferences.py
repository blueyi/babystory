
# Copyright (C) 2013 LiuLang <gsushzhsosgsu@gmail.com>

# Use of this source code is governed by GPLv3 license that can be found
# in http://www.gnu.org/licenses/gpl-3.0.html

from gi.repository import Gtk
import os

from babystory import Widgets

class NoteTab(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.set_border_width(10)


class Preferences(Gtk.Dialog):
    def __init__(self, app):
        self.app = app
        super().__init__('Preferences', app.window, 0,
                (Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE, ))
        self.set_modal(True)
        self.set_transient_for(app.window)
        self.set_default_size(600, 320)
        self.set_border_width(5)
        box = self.get_content_area()

        folder_box = NoteTab()
        box.pack_start(folder_box, False, False, 0)

        folder_label = Widgets.BoldLabel('Place to store songs')
        folder_box.pack_start(folder_label, False, False, 0)

        folder_chooser_box = Gtk.Box()
        folder_box.pack_start(folder_chooser_box, False, False, 0)

        self.chooser_entry = Gtk.Entry(text=app.conf['song-dir'])
        self.chooser_entry.props.editable = False
        self.chooser_entry.props.width_chars = 20
        self.chooser_entry.props.can_focus = False
        folder_chooser_box.pack_start(self.chooser_entry, True, True, 0)

        chooser_button = Gtk.Button('...')
        chooser_button.connect('clicked', self.on_chooser_button_clicked)
        folder_chooser_box.pack_start(chooser_button, False, False, 0)

        box.show_all()

    def on_chooser_button_clicked(self, button):
        def on_dialog_file_activated(dialog):
            new_dir = dialog.get_filename()
            dialog.destroy()
            self.chooser_entry.set_text(new_dir)
            self.app.conf['song-dir'] = new_dir
            return

        dialog = Gtk.FileChooserDialog('Choose a Folder', self.app.window,
                Gtk.FileChooserAction.SELECT_FOLDER,
                (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                    Gtk.STOCK_OK, Gtk.ResponseType.OK))

        dialog.connect('file-activated', on_dialog_file_activated)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            on_dialog_file_activated(dialog)
            return
        dialog.destroy()
