#!/usr/bin/env python
# -*- coding: utf-8 -*-
# jnrain-ng / dida / socket.io namespace
#
# Copyright (C) 2013 JNRainerds
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from __future__ import unicode_literals, division

import time
import cgi

from socketio.namespace import BaseNamespace
from socketio.mixins import RoomsMixin, BroadcastMixin

from weiyu.async import async_hub

from .state import getstate
from .log import i, w
from .kbshelper import chkpasswd
from .heartbeat import run_heartbeat_thread_once


@async_hub.register_ns('socketio', '')
class ChatNamespace(BaseNamespace, RoomsMixin, BroadcastMixin):
    def on_login(self, data):
        username, passwd = data['username'], data['psw']

        try:
            loginok = chkpasswd(username.lower(), passwd)
        except KeyError:
            loginok = False

        if not loginok:
            w('LOGINFAIL %s %s' % (
                username,
                passwd,
                ))
            return [1, ]

        if username in getstate()['nicknames']:
            return [2, ]

        i('LOGIN %s' % (username, ))

        with getstate()['freshlock']:
            getstate()['nicknames'].append(username)
            getstate()['freshnesses'][username] = time.time()

        self.socket.session['nickname'] = username
        self.broadcast_event('announcement', u'%s 已上线' % username, time.time())
        self.broadcast_event('nicknames', getstate()['nicknames'])
        # Just have them join a default-named room
        self.join('main_room')

        # Run heartbeat cleaner if there isn't one
        run_heartbeat_thread_once(self)

        return [0, ]

    def recv_disconnect(self):
        # Remove nickname from the list.
        try:
            nickname = self.socket.session['nickname']
        except KeyError:
            return

        i('LOGOUT %s' % (nickname, ))

        try:
            with getstate()['freshlock']:
                getstate()['nicknames'].remove(nickname)
                getstate()['freshnesses'].pop(nickname)
        except KeyError:
            pass

        self.broadcast_event('announcement', u'%s 已下线' % nickname, time.time())
        self.broadcast_event('nicknames', getstate()['nicknames'])

        self.disconnect(silent=True)

    def on_user_message(self, msg):
        msg = cgi.escape(msg)
        i('MSG %s %s'  % (
            self.socket.session['nickname'],
            msg,
            ))

        self.emit_to_room('main_room', 'msg_to_room',
            self.socket.session['nickname'], msg, time.time())

    def on_heartbeat(self):
        getstate()['freshnesses'][self.socket.session['nickname']] = time.time()


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
