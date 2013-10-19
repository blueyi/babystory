
# Copyright (C) 2013 LiuLang <gsushzhsosgsu@gmail.com>

# Use of this source code is governed by GPLv3 license that can be found
# in http://www.gnu.org/licenses/gpl-3.0.html

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
