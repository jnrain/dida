#!/usr/bin/env python
# -*- coding: utf-8 -*-
# jnrain-ng / dida / heartbeat
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
import threading

from .state import getstate
from .log import d, e

CHECK_INTERVAL, HEARTBEAT_TIMEOUT = 3, 30


def heartbeat_cleaner(ns):
    d('CLEANERSTART')
    state = getstate()

    while not state['close_evt'].is_set():
        time.sleep(CHECK_INTERVAL)

        curtime = time.time()
        freshnesses, nicknames = state['freshnesses'], state['nicknames']
        # logfile.write('%d CLEAN %d users\n' % (curtime, len(freshnesses), ))
        for user in nicknames:
            try:
                last_active = freshnesses[user]
            except KeyError:
                # Inconsistent freshness, this should not happen
                # In case it really bites, set the user to be cleaned
                e('PURGEERR -- No freshness for %s' % (user, ))
                last_active = 0.0

            if curtime - last_active > HEARTBEAT_TIMEOUT:
                # Purge the user.
                d('PURGEUSR %s (%.4f)' % (user, last_active, ))
                try:
                    with state['freshlock']:
                        freshnesses.pop(user)
                        state['nicknames'].remove(user)
                except KeyError:
                    pass

                # Notify the users.
                ns.broadcast_event(
                        'announcement',
                        '%s 已掉线' % (user, ),
                        time.time(),
                        )
                ns.broadcast_event('nicknames', state['nicknames'])

        # flush log periodically
        # logfile.flush()

    # app exiting
    d('CLEANEREXIT')


def get_heartbeat_thread(ns=None):
    state = getstate()

    try:
        return state['_heartbeat_thread']
    except KeyError:
        if ns is None:
            raise ValueError('please instantiate with meaningful parameters')

        thrd = threading.Thread(target=heartbeat_cleaner, args=(ns, ))
        state['_heartbeat_thread'] = thrd

        return thrd


def run_heartbeat_thread_once(ns, __running=[]):
    thrd = get_heartbeat_thread(ns)
    if not __running:
        thrd.start()
        __running.append(1)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
