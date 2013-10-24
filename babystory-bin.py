#!/usr/bin/env python3

# Copyright (C) 2013 LiuLang <gsushzhsosgsu@gmail.com>

# Use of this source code is governed by GPLv3 license that can be found
# in the LICENSE file.

import sys

from babystory.App import App


def main():
    app = App()
    sys.exit(app.run(sys.argv))

if __name__ == '__main__':
    main()
