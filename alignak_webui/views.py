#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2015:
#   Frederic Mohier, frederic.mohier@gmail.com
#
# This file is part of (WebUI).
#
# (WebUI) is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# (WebUI) is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with (WebUI).  If not, see <http://www.gnu.org/licenses/>.

"""
Main application views and routes
"""
# import flask
from flask import Flask
from flask import session, redirect, url_for, escape, request
from flask import render_template, flash, get_flashed_messages, g
from flask_login import login_required, current_user

from alignak_webui import app, manifest
from alignak_webui.user import User
from alignak_webui.utils.helper import helper


@app.route('/')
@app.route('/index')
@login_required
def index():
    """
    Application home page

    Only authenticated users can see this page
    """
    app.logger.info("show home page ...")
    app.logger.info("current_user: %s / %s", type(current_user), current_user)

    return render_template(
        'home-page.html',
        user=current_user,
        helper=helper,
        manifest=manifest,
        settings=app.config
    )


# Shutdown Web server ...
def shutdown_server():
    """ ../.. """
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    # pragma: no cover - impossible to reach with unit testing ...
    func()


@app.route('/shutdown', methods=['POST'])
def shutdown():
    """ ../.. """
    shutdown_server()
    return 'Server shutting down...'
