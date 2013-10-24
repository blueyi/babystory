关于
====
babystory 是可以给小宝宝们讲故事, 唱儿歌的软件.

现在有不少80后的朋友都有了孩子, 但是与成人世界不同, 适合宝宝们听的儿歌啦,
故事啦都算是稀缺的资源. 而在Linux桌面上就更难找了.

babystory目前可播放近五千首儿歌和故事.

缺点也是有的, 比如有些音频文件的质量不高.

自动安装
========
目前只为debian系统提供了deb安装包, 适合其它发行版的, 之后会陆续加入.
可以在这里直接下载打好的[安装包](https://github.com/LiuLang/babystory-packages)


手动安装
====
分两步, 一是安装依赖包, 二是安装软件本身.

babystory使用了[kwplayer](https://github.com/LiuLang/kwplayer)的框架, 如果
你已经安装了的话, 就不需要再处理依赖包的问题了, 请直接转到第二步.

Debian tesint/sid 系统里, babystory的依赖包有:

* python3-gi
* gstreamer1.0-plugins-base
* gstreamer1.0-plugins-good
* gstremaer1.0-plguins-ugly
* gir1.2-gstreamer-1.0
* gir1.2-gst-plugins-base-1.0
* python3-mutagenx 解决mp3文件乱码问题的, 需要python3.3以上的版本, 这个包不
是必需的.
* gnome-icon-theme-symbolic 图标

如果系统里没有gstreamer1.0, 请将上面列出的几个gstreamer的版本改成0.10.

Arch Linux系的话, 大概是这样的:
* python-gobject
* gstreamer
* gst-plugins-base
* gst-plugins-good
* gst-plugins-ugly
* gnome-icon-theme-symbolic
* python3-mutagenx


第二步, 安装babystory本身.  

* 安装: `# pip3 install babystory`
* 更新: `# pip3 iinstall upgrade babystory`

SCREENSHOTS
===========
专辑分类:
<img src="screenshots/categories.jpg?raw=true" title="专辑分类" />

播放列表:
<img src="screenshots/playlists.jpg?raw=true" title="播放列表" />


COPYRIGHT
=========
`Copyright (C) 2013 LiuLang <gsushzhsosgsu@gmail.com>`
软件本身使用 GNU Plublic License v3协议发布, 协议内容请参看LICENSE文件.

本人不存储任何多媒体资源供其他人下载, 软件会从网络中下载文件.
如果发生版权纠纷, 使用者本人(或其监护人)将承担相应的责任.
