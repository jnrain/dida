#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division

from hashlib import md5

KBS_PASSMAGIC = r'wwj&kcn4SMTHBBS MD5 p9w2d gen2rat8, //grin~~, 2001/5/7'


def kbs_encode(userid, passwd, passmagic=KBS_PASSMAGIC):
    # XXX Must not be permissive here, or this explicit encoding will
    # instantly become a vulnerability!!
    data = ''.join([passmagic, passwd, passmagic, userid, ]).encode('utf-8')
    return md5(data).digest()


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
