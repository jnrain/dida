#!/usr/bin/env python
# -*- coding: utf-8 -*-
# jnrain-ng / dida / WSGI stub
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


from gevent import monkey; monkey.patch_all()

from weiyu.shortcuts import inject_app
from weiyu.utils.server import cli_server

from dida.state import initstate


inject_app()
initstate()


if __name__ == '__main__':
    cli_server(
            'socketio',
            ('0.0.0.0', 8080),
            resource="socket.io",
            policy_server=True,
            policy_listener=('0.0.0.0', 10843),
            )


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
