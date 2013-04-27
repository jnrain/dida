#!/usr/bin/env python
# -*- coding: utf-8 -*-
# jnrain-ng / dida / views
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

from weiyu.shortcuts import http, renderable, view


@http('index')
@renderable('mako', 'chat.html')
@view
def index_view(request):
    return (
            200,
            {},
            {
                'mimetype': 'text/html',
                'enc': 'utf-8',
                },
            )


@http('404')
@renderable('mako', '404.html')
@view
def http404_view(request):
    return (
            404,
            {},
            {
                'mimetype': 'text/html',
                'enc': 'utf-8',
                },
            )


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
