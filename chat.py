#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gevent import monkey; monkey.patch_all()

import sys
import time
import cgi
import threading
import atexit

from socketio import socketio_manage
from socketio.server import SocketIOServer
from socketio.namespace import BaseNamespace
from socketio.mixins import RoomsMixin, BroadcastMixin

from chkpasswd import chkpasswd

HEARTBEAT_TIMEOUT = 60


def tostr(s):
    if isinstance(s, str):
        return s
    return s.encode('utf-8', 'replace')


def heartbeat_cleaner(ns, request):
    logfile = request['logfile']
    logfile.write('%d CLEANERSTART\n' % (time.time(), ))
    logfile.flush()

    while not request['close_evt'].is_set():
        time.sleep(HEARTBEAT_TIMEOUT)

        curtime = time.time()
        freshnesses, nicknames = request['freshnesses'], request['nicknames']
        # logfile.write('%d CLEAN %d users\n' % (curtime, len(freshnesses), ))
        for user in nicknames:
            try:
                last_active = freshnesses[user]
            except KeyError:
                # Inconsistent freshness, this should not happen
                # In case it really bites, set the user to be cleaned
                logfile.write(
                        '%d PURGEERR -- No freshness for %s\n' % (
                            time.time(),
                            tostr(user),
                            )
                        )
                last_active = 0.0

            if curtime - last_active > HEARTBEAT_TIMEOUT:
                # Purge the user.
                logfile.write(
                        '%d PURGEUSR %s (%.4f)\n' % (
                            time.time(),
                            tostr(user),
                            last_active,
                            )
                        )
                try:
                    with request['freshlock']:
                        freshnesses.pop(user)
                        request['nicknames'].remove(user)
                except KeyError:
                    pass

                # Notify the users.
                ns.broadcast_event(
                        'announcement',
                        u'%s 已掉线' % (user, ),
                        time.time(),
                        )
                ns.broadcast_event('nicknames', request['nicknames'])

        # flush log periodically
        # logfile.flush()

    # app exiting
    logfile.write('%d CLEANEREXIT\n' % (time.time(), ))


def get_heartbeat_thread(ns=None, request=None, __thread=[]):
    if __thread:
        # there is already a thread
        return __thread[0]

    if ns is None and request is None:
        raise ValueError('please instantiate with meaningful parameters')

    thrd = threading.Thread(target=heartbeat_cleaner, args=(ns, request))

    __thread.append(thrd)
    return thrd


def run_heartbeat_thread_once(ns, request, __running=[]):
    thrd = get_heartbeat_thread(ns, request)
    if not __running:
        thrd.start()
        __running.append(1)


class ChatNamespace(BaseNamespace, RoomsMixin, BroadcastMixin):
    def on_login(self, data):
        username, passwd = data['username'], data['psw']

        try:
            loginok = chkpasswd(username.lower(), passwd)
        except KeyError:
            loginok = False

        if not loginok:
            self.request['logfile'].write('%d LOGINFAIL %s %s\n' % (
                time.time(),
                tostr(username),
                tostr(passwd),
                ))
            self.request['logfile'].flush()
            return [1, ]

        if username in self.request['nicknames']:
            return [2, ]

        self.request['logfile'].write('%d LOGIN %s\n' % (time.time(), tostr(username)))
        self.request['logfile'].flush()

        with self.request['freshlock']:
            self.request['nicknames'].append(username)
            self.request['freshnesses'][username] = time.time()

        self.socket.session['nickname'] = username
        self.broadcast_event('announcement', u'%s 已上线' % username, time.time())
        self.broadcast_event('nicknames', self.request['nicknames'])
        # Just have them join a default-named room
        self.join('main_room')

        # Run heartbeat cleaner if there isn't one
        run_heartbeat_thread_once(self, self.request)

        return [0, ]

    def recv_disconnect(self):
        # Remove nickname from the list.
        try:
            nickname = self.socket.session['nickname']
        except KeyError:
            return

        self.request['logfile'].write('%d LOGOUT %s\n' % (time.time(), tostr(nickname)))
        self.request['logfile'].flush()

        try:
            with self.request['freshlock']:
                self.request['nicknames'].remove(nickname)
                self.request['freshnesses'].pop(nickname)
        except KeyError:
            pass

        self.broadcast_event('announcement', u'%s 已下线' % nickname, time.time())
        self.broadcast_event('nicknames', self.request['nicknames'])

        self.disconnect(silent=True)

    def on_user_message(self, msg):
        msg = cgi.escape(msg)
        self.request['logfile'].write('%d MSG %s %s\n'  % (
            time.time(),
            tostr(self.socket.session['nickname']),
            tostr(msg),
            ))
        self.request['logfile'].flush()

        self.emit_to_room('main_room', 'msg_to_room',
            self.socket.session['nickname'], msg, time.time())

    def on_heartbeat(self):
        self.request['freshnesses'][self.socket.session['nickname']] = time.time()

    def recv_message(self, message):
        print "PING!!!", message


class Application(object):
    def __init__(self):
        self.buffer = []
        # Dummy request object to maintain state between Namespace
        # initialization.
        self.request = {
            'nicknames': [],
            'freshnesses': {},
            'freshlock': threading.Lock(),
            'logfile': open('chat.log', 'a+b'),
            'close_evt': threading.Event(),
        }

        # atexit cleaner for proper termination of heartbeat thread
        def _cleanup_things():
            self.request['close_evt'].set()
            get_heartbeat_thread().join()
            self.request['logfile'].close()

        atexit.register(_cleanup_things)

    def __call__(self, environ, start_response):
        path = environ['PATH_INFO'].strip('/')

        if not path:
            start_response('200 OK', [('Content-Type', 'text/html')])
            return ['<h1>滴答——听雨在线聊天实验原型，欢迎试用。'
                '<a href="/chat.html">点这里进入页面</a>。</h1>']

        if path.startswith('static/') or path == 'chat.html':
            try:
                data = open(path).read()
            except Exception:
                return not_found(start_response)

            if path.endswith(".js"):
                content_type = "text/javascript"
            elif path.endswith(".css"):
                content_type = "text/css"
            elif path.endswith(".swf"):
                content_type = "application/x-shockwave-flash"
            else:
                content_type = "text/html"

            start_response('200 OK', [('Content-Type', content_type)])
            return [data]

        if path.startswith("socket.io"):
            socketio_manage(environ, {'': ChatNamespace}, self.request)
        else:
            return not_found(start_response)


def not_found(start_response):
    start_response('404 Not Found', [])
    return ['<h1>Not Found</h1>']


if __name__ == '__main__':
    SocketIOServer(
            ('127.0.0.1', 10088),
            Application(),
            resource="socket.io",
            policy_server=True,
            policy_listener=('0.0.0.0', 10843),
            #heartbeat_interval=30,
            #heartbeat_timeout=60,
            ).serve_forever()


# vim:ai:et:ts=4:sw=4:sts=4:
