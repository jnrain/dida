#!/usr/bin/env python
# -*- coding: utf-8 -*-
# jnrain-ng / dida / logging
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
        'get_logfile',
        'log',
        'v',
        'd',
        'i',
        'w',
        'e',
        'f',
        ]

import time
from functools import partial

from .state import getstate

LOGFILE_KEY = 'logfile'


def get_logfile():
    return getstate()[LOGFILE_KEY]


def log(level, msg):
    logfile = get_logfile()
    logfile.write(b'%d %s %s\n' % (
        time.time(),
        level,
        msg.encode('utf-8', 'replace') if isinstance(msg, unicode) else msg,
        ))
    logfile.flush()


v = partial(log, b'V')  # verbose
d = partial(log, b'D')  # debug
i = partial(log, b'I')  # info
w = partial(log, b'W')  # warning
e = partial(log, b'E')  # error
f = partial(log, b'F')  # fatal


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
