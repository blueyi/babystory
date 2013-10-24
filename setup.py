#!/usr/bin/env python3

# Copyright (C) 2013 LiuLang <gsushzhsosgsu@gmail.com>

# Use of this source code is governed by GPLv3 license that can be found
# in http://www.gnu.org/licenses/gpl-3.0.html

# Distutils script for babystory
from distutils.core import setup
import os

from babystory import Config


def build_data_files():
    data_files = []
    for dir, dirs, files in os.walk('share'):
        #target = os.path.join('share', dir)
        target = dir
        if files:
            files = [os.path.join(dir, f) for f in files]
            data_files.append((target, files))
    return data_files


if __name__ == '__main__':
    setup(
        name = 'babystory',
        version = Config.VERSION,
        description = Config.DESCRIPTION,
        long_description = Config.LONG_DESC,
        url = Config.HOMEPAGE,
        license = 'GPLv3',

        author = 'LiuLang',
        author_email = 'gsushzhsosgsu@gmail.com',

        packages = ['babystory', ],
        scripts = ['babystory.py', ],
        data_files = build_data_files(),
        )
