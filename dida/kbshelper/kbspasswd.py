#!/usr/bin/env python
# -*- coding: utf-8 -*-
# jnrain-ng / dida / KBS interop helper / KBS password hash
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

from hashlib import md5

KBS_PASSMAGIC = r'wwj&kcn4SMTHBBS MD5 p9w2d gen2rat8, //grin~~, 2001/5/7'


def kbs_encode(userid, passwd, passmagic=KBS_PASSMAGIC):
    # XXX Must not be permissive here, or this explicit encoding will
    # instantly become a vulnerability!!
    data = ''.join([passmagic, passwd, passmagic, userid, ]).encode('utf-8')
    return md5(data).digest()


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
