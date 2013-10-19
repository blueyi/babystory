
# Copyright (C) 2013 LiuLang <gsushzhsosgsu@gmail.com>

# Use of this source code is governed by GPLv3 license that can be found
# in http://www.gnu.org/licenses/gpl-3.0.html

import gettext
from gi.repository import GdkPixbuf
import json
import locale
import os
import shutil


if __file__.startswith('/usr/'):
    PREF = '/usr/share'
else:
    PREF = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'share')

LOCALEDIR = os.path.join(PREF, 'locale')
gettext.bindtextdomain('babystory', LOCALEDIR)
gettext.textdomain('babystory')
locale.bindtextdomain('babystory', LOCALEDIR)
locale.textdomain('babystory')
_ = gettext.gettext

APPNAME = _('Baby Story')
VERSION = '1.0'
HOMEPAGE = 'https://github.com/LiuLang/babystory'
AUTHORS = ['LiuLang <gsushzhsosgsu@gmail.com>',]
COPYRIGHT = 'Copyright (c) 2013 LiuLang'
DESCRIPTION = 'Baby Story is a '

HOME_DIR = os.path.expanduser('~')
CACHE_DIR = os.path.join(HOME_DIR, '.cache', 'babystory')
IMG_DIR = os.path.join(CACHE_DIR, 'images')
SONG_LIST_DIR = os.path.join(CACHE_DIR, 'songlists')
PLS_JSON = os.path.join(CACHE_DIR, 'pls.json')
CAT_JSON = os.path.join(CACHE_DIR, 'cat.json')

THEME_DIR = os.path.join(PREF, 'babystory', 'themes', 'default')
DEFAULT_CAT_JSON = os.path.join(PREF, 'babystory', 'default_cat.json')

CONF_DIR = os.path.join(HOME_DIR, '.config', 'babystory')
_conf_file = os.path.join(CONF_DIR, 'conf.json')

_default_conf = {
        'window-size': (840, 580),
        'song-dir': os.path.join(CACHE_DIR, 'song'),
        'volume': 0.08,
        'use-status-icon': True,
        }

def check_first():
    if not os.path.exists(CONF_DIR):
        try:
            os.mkdir(CONF_DIR)
        except Exception as e:
            print(e)
            sys.exit(1)
    if not os.path.exists(CACHE_DIR):
        try:
            os.mkdir(CACHE_DIR)
            os.mkdir(IMG_DIR)
            os.mkdir(_default_conf['song-dir'])
            os.mkdir(SONG_LIST_DIR)
        except Exception as e:
            print(e)
            sys.exit(1)

def load_conf():
    if os.path.exists(_conf_file):
        with open(_conf_file) as fh:
            conf = json.loads(fh.read())
        for key in _default_conf:
            if key not in conf:
                conf[key] = _default_conf[key]
        return conf
    dump_conf(_default_conf)
    return _default_conf

def dump_conf(conf):
    with open(_conf_file, 'w') as fh:
        fh.write(json.dumps(conf, indent=2))

def load_theme():
    theme_file = os.path.join(THEME_DIR, 'images.json')
    try:
        with open(theme_file) as fh:
            theme = json.loads(fh.read())
    except Exception as e:
        print(e)
        return None

    theme_pix = {}
    for key in theme:
        filename = os.path.join(THEME_DIR, theme[key])
        if os.path.exists(filename):
            theme_pix[key] = GdkPixbuf.Pixbuf.new_from_file(filename)
        else:
            print('Failed to open theme icon', filename)
            return None
    return theme_pix

def load_category_list():
    if not os.path.exists(CAT_JSON):
        shutil.copy(DEFAULT_CAT_JSON, CAT_JSON)
    with open(CAT_JSON) as fh:
        return json.loads(fh.read())

def dump_category_list(category_list):
    with open(CAT_JSON, 'w') as fh:
        fh.write(json.dumps(category_list, indent=2))

_default_playlist = []
def load_playlist():
    if not os.path.exists(PLS_JSON):
        dump_playlist(_default_playlist)
        return _default_playlist
    with open(PLS_JSON) as fh:
        return json.loads(fh.read())

def dump_playlist(playlist):
    with open(PLS_JSON, 'w') as fh:
        fh.write(json.dumps(playlist, indent = 2))
