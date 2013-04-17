#!/usr/bin/env python
# -*- coding: utf-8 -*-

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


# vi:ai:et:ts=4 sw=4 sts=4 fenc=utf-8 ff=unix
