
# Copyright (C) 2013 LiuLang <gsushzhsosgsu@gmail.com>

# Use of this source code is governed by GPLv3 license that can be found
# in http://www.gnu.org/licenses/gpl-3.0.html

import os
import sys

mutagenx_imported = False
if sys.version_info.major >= 3 and sys.version_info.minor >= 3:
    try:
        from mutagenx import id3
        mutagenx_imported = True
    except ImportError as e:
        print('Warning: mutagenx was not found')
else:
    print('Warning: Python3 < 3.3, mutagenx is not supported')


def print_size(size):
    return '{0:.1f}M'.format(size/1048576)

def print_duration(duration):
    mm, ss = divmod(duration, 60)
    return '{0:02d}:{1:02d}'.format(mm, ss)

def print_nano_duration(nanosec_float):
    _seconds = nanosec_float // 10**9
    mm, ss = divmod(_seconds, 60)
    hh, mm = divmod(mm, 60)
    if hh == 0:
        s = '%d:%02d' % (mm, ss)
    else:
        s = '%d:%02d:%02d' % (hh, mm, ss)
    return s


def iconvtag(song_path, song):
    # Do nothing if python3 version is lower than 3.3
    if not mutagenx_imported:
        return
    print('Net.iconvtag()', song_path, song)
    def use_id3():
        id3.delete(song_path)
        audio = id3.ID3()
        audio.add(id3.TIT2(encoding=3, text=song['Title']))
        audio.add(id3.TALB(encoding=3, text=song['Category']))
        audio.save(song_path)

    ext = os.path.splitext(song_path)[1].lower()
    if ext == '.mp3':
        use_id3()
    else:
        print('icontag does not support this format:', song, song_path)
