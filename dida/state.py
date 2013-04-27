#!/usr/bin/env python
# -*- coding: utf-8 -*-
# jnrain-ng / dida / state management
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

__all__ = [
        'getstate',
        'initstate',
        ]

import atexit
import threading

from weiyu.registry.provider import request as regrequest
from weiyu.registry.classes import UnicodeRegistry

REG_NAME = 'jnrain.dida'


def getstate():
    return regrequest(REG_NAME)


def initstate():
    # this should create a new registry
    state = regrequest(REG_NAME, autocreate=True, klass=UnicodeRegistry)

    state['nicknames'] = []
    state['freshnesses'] = {}
    state['freshlock'] = threading.Lock()
    state['logfile'] = open('chat.log', 'a+b')
    state['close_evt'] = threading.Event()

    # atexit cleaner for proper termination of heartbeat thread
    def _cleanup_things():
        state = getstate()
        state['close_evt'].set()
        state['_heartbeat_thread'].join()
        state['logfile'].close()

    atexit.register(_cleanup_things)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
