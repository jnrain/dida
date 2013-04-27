#!/usr/bin/env python
# -*- coding: utf-8 -*-
# jnrain-ng / dida / KBS interop helper / password checker
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

from os.path import realpath, split as pathsplit
from os.path import join as pathjoin

from cPickle import loads

from kbspasswd import kbs_encode

DATA_FILE = realpath(pathjoin(pathsplit(__file__)[0], 'PASSWDS.pickle'))


def build_dict():
    with open(DATA_FILE, 'rb') as fp:
        content = fp.read()

    return loads(content)


_dict = build_dict()


def chkpasswd(uid, psw):
    return _dict[uid] == kbs_encode(uid, psw)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
