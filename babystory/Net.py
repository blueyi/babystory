
# Copyright (C) 2013 LiuLang <gsushzhsosgsu@gmail.com>

# Use of this source code is governed by GPLv3 license that can be found
# in http://www.gnu.org/licenses/gpl-3.0.html

from gi.repository import GdkPixbuf
from gi.repository import GObject
import json
import os
import threading
import urllib.error
import urllib.request
import urllib.parse

from babystory import Config
from babystory import Utils

GObject.threads_init()

CHUNK = 2 ** 14
CHUNK_TO_PLAY = 2 ** 21     # 2M
MAXTIMES = 3
SERVER_REQ = 'http://baby.moguwa.com/do.asp'
TIMEOUT = 30

def empty_func(*args, **kwds):
    pass

# calls f on another thread
def async_call(func, func_done, *args):
    def do_call(*args):
        result = None
        error = None

        try:
            result = func(*args)
        except Exception as e:
            error = e

        GObject.idle_add(lambda: func_done(result, error))

    thread = threading.Thread(target=do_call, args=args)
    thread.start()

opener = urllib.request.build_opener()
opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
def urlopen(url, data=None):
    for retried in range(MAXTIMES):
        try:
            req = opener.open(url, data=data, timeout=TIMEOUT)
            return req.read()
        except Exception as e:
            print('Error: Net.urlopen', e, 'with url:', url)
    return None

def query(param):
    _param = urllib.parse.urlencode(param).encode()
    url = SERVER_REQ
    req_content = urlopen(url, data=_param)
    if req_content is None:
        return None
    return req_content.decode('gbk')

def get_categories(cat_id):
    param = {
            'ClientOS': 'Android 2.3.7',
            'Action': 'GetStoryCategorysWithNewVersion',
            'ArgLen': 2,
            'Arg1': cat_id,
            'Arg2': 0,
            }
    return json.loads(query(param))

def get_songs(cat_id):
    filepath = os.path.join(Config.SONG_LIST_DIR, str(cat_id) + '.json')
    if os.path.exists(filepath):
        with open(filepath) as fh:
            return json.loads(fh.read())

    param = {
            'ClientOS': 'Android 2.3.7',
            'Action': 'GetStorysWithNewVersion',
            'ArgLen': 2,
            'Arg1': cat_id,
            'Arg2': 0,
            }
    songs_wrap = query(param)
    if songs_wrap is None:
        return None
    with open(filepath, 'w') as fh:
        fh.write(songs_wrap)
    return json.loads(songs_wrap)

def get_hot_songs(cat_id, num_of_songs=20):
    param = {
            'ClientOS': 'Android 2.3.7',
            'Action': 'GetHotStorys',
            'ArgLen': 2,
            'Arg1': cat_id,
            'Arg2': num_of_songs,
            }
    return query(param)

def get_image(url):
    img_name = os.path.split(url)[1]
    img_path = os.path.join(Config.IMG_DIR, img_name)
    if os.path.exists(img_path):
        return img_path
    img = urlopen(url)
    if img is None:
        return None
    with open(img_path, 'wb') as fh:
        fh.write(img)
    return img_path

def update_liststore_image(liststore, path, col, url):
    def _update_image(filepath, error=None):
        if filepath is None or error:
            return
        try:
            pix = GdkPixbuf.Pixbuf.new_from_file_at_size(filepath, 150, 80)
            liststore[path][col] = pix
        except Exception as e:
            print('Error: Net.update_liststore_image:', e, 
                    'with filepath:', filepath, 'url:', url)

    async_call(get_image, _update_image, url)


class AsyncSong(GObject.GObject):
    '''
    Use Gobject to emit signals:
    register three signals: can-play and downloaded
    if `can-play` emited, player will receive a filename which have
    at least 1M to play.
    `chunk-received` signal is used to display the progressbar of 
    downloading process.
    `downloaded` signal may be used to popup a message to notify 
    user that a new song is downloaded.
    '''
    __gsignals__ = {
            'can-play': (GObject.SIGNAL_RUN_LAST, 
                # sogn_path, state
                GObject.TYPE_NONE, (str, str)),
            'chunk-received': (GObject.SIGNAL_RUN_LAST,
                # percent
                GObject.TYPE_NONE, (int, )),
            'downloaded': (GObject.SIGNAL_RUN_LAST, 
                # song_path
                GObject.TYPE_NONE, (str, ))
            }
    def __init__(self, app):
        print('AsyncSong.__init__()')
        super().__init__()
        self.app = app
        self.force_quit = False

    def destroy(self):
        self.force_quit = True

    def get_song(self, song):
        print('AsyncSong.get_song()')
        async_call(self._download_song, empty_func, song)

    def get_song_path(self, song):
        return os.path.join(self.app.conf['song-dir'],
                song['category']['Title'],
                song['Title'] + os.path.splitext(song['Url'])[1])

    def _download_song(self, song):
        def _wrap(req):
            received_size = 0
            can_play_emited = False
            content_length = int(req.headers.get('Content-Length'))
            print('size of file: ', round(content_length / 2**20, 2), 'M')
            fh = open(song_path, 'wb')

            while True:
                if self.force_quit:
                    del req
                    fh.close()
                    os.remove(song_path)
                    return False
                chunk = req.read(CHUNK)
                received_size += len(chunk)
                percent = int(received_size/content_length * 100)
                self.emit('chunk-received', percent)
                #print('percentage:', percent)
                # this signal only emit once.
                if (received_size > CHUNK_TO_PLAY or percent > 40) \
                        and not can_play_emited:
                    print('song can be played now')
                    can_play_emited = True
                    self.emit('can-play', song_path, 'OK')
                if not chunk:
                    break
                fh.write(chunk)

            fh.close()
            print('song downloaded')
            self.emit('downloaded', song_path)
            Utils.iconvtag(song_path, song)
            return True

        song_link = song['Url']
        song_path = self.get_song_path(song)

        if os.path.exists(song_path):
            print('local song exists, signals will be emited:', song_path)
            self.emit('can-play', song_path, 'OK')
            self.emit('downloaded', song_path)
            return

        song_dir = os.path.split(song_path)[0]
        if not os.path.exists(song_dir):
            os.makedirs(song_dir)

        print('Net.AsyncSong, song will be downloaded:', song_path)
        for retried in range(MAXTIMES):
            try:
                req = urllib.request.urlopen(song_link)
                state = _wrap(req)
                if state:
                    return
            except Exception as e:
                print('AsyncSong._download_song()', e, 'with song_link:',
                        song_link)
        print('song failed to download, please check link', song_link)
        if os.path.exists(song_path):
            os.remove(song_path)
            self.emit('can-play', song_path, 'URLError')
        else:
            self.emit('can-play', song_path, 'FileNotFoundError')
        self.emit('downloaded', None)
        return None
GObject.type_register(AsyncSong)
