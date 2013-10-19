
# Copyright (C) 2013 LiuLang <gsushzhsosgsu@gmail.com>

# Use of this source code is governed by GPLv3 license that can be found
# in http://www.gnu.org/licenses/gpl-3.0.html

from gi.repository import Gtk

from babystory import Config
_ = Config._


class ExpandedTreeViewColumn(Gtk.TreeViewColumn):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.props.sizing = Gtk.TreeViewColumnSizing.FIXED
        self.props.min_width = 150
        self.props.expand = True

def network_error(parent, msg):
    dialog = Gtk.MessageDialog(parent, Gtk.DialogFlags.MODAL,
            Gtk.MessageType.ERROR, Gtk.ButtonsType.CLOSE,
            msg)
    dialog.format_secondary_text(
            _('Please check network connection and try again'))
    dialog.run()
    dialog.destroy()

def filesystem_error(parent, path):
    msg = _('Failed to open file or direcotry')
    dialog = Gtk.MessageDialog(parent, Gtk.DialogFlags.MODAL,
            Gtk.MessageType.ERROR, Gtk.ButtonsType.CLOSE,
            msg)
    dialog.format_secondary_text(
            _('Please check {0} exists').format(path))
    dialog.run()
    dialog.destroy()
