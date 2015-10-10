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
from flask import session, redirect, url_for, escape, request, make_response
from flask import render_template, flash, get_flashed_messages, g, jsonify
from flask_login import login_required, current_user

from alignak_webui import app, manifest, frontend
from alignak_webui.user import User
from alignak_webui.utils.helper import helper
from alignak_webui.datatable import DatatableException


@app.context_processor
def inject_variables():
    """
        All templates rendered in the application will automatically inherit from all the variables
        defined in the returned dictionary:
        - user is the current logged in user
        - helper is an instance of Helper class
        - manifest is the application information dictionary
        - settings is the current application configuration
    """
    return dict(
        user=current_user,
        helper=helper,
        manifest=manifest,
        settings=app.config
    )


@app.route('/ping', methods=['GET'])
def ping():
    """ Is server alive? """
    return 'pong'


@app.route('/search_string', methods=['GET', 'POST'])
def set_search_string():
    """
    Set search string ...

    If GET request, returns UI data:
    - search_string

    If POST request, update UI data
    - search_string
    """
    app.logger.info("Helper search string: %s", helper)
    if request.method == 'POST':
        helper.search_string = request.form['search_string']
        app.logger.info("New helper search string: %s", helper.search_string)
        return str(helper.search_string)

    if request.method == 'GET':
        data = {"search_string": helper.search_string}
        res = jsonify(**data)
        res.status_code = 200
        return res


@app.route('/')
@app.route('/index')
@login_required
def index():
    """
    Application home page

    Only authenticated users can see this page
    """
    app.logger.info("show home page ...")

    return render_template(
        'home-page.html'
    )


@app.route('/refresh_header')
@login_required
def refresh_header():
    """
    Refresh application page header

    Update system live synthesis and build header elements
    """
    data = {'livesynthesis': helper.get_html_livesynthesis()}

    res = jsonify(**data)
    res.status_code = 200
    return res


@app.route('/refresh_livestate')
@login_required
def refresh_livestate():
    """
    Refresh application livestate

    Update system live state and build header elements
    """
    data = {'livestate': helper.get_html_livestate(int(request.args.get('bi', 0)))}

    res = jsonify(**data)
    res.status_code = 200
    return res


@app.route('/livesynthesis')
@login_required
def get_livesynthesis():
    """
    Get application livestate synthesis

    """
    data = {'livesynthesis': helper.get_livesynthesis()}

    res = jsonify(**data)
    res.status_code = 200
    return res


@app.errorhandler(401)
def custom_401(error):  # pragma: no cover
    """
    Custom 401 error
    """
    resp = make_response(u"Access is denied without logging in", error)
    resp.headers['WWWAuthenticate'] = 'Basic realm="Login Required"'
    return resp


@app.errorhandler(DatatableException)
def custom_DatatableException(error):  # pragma: no cover
    """
    Custom Datatable error
    """
    app.logger.debug("custom_DatatableException: %s", error)
    return make_response(u"Exception ...", 450)


@app.errorhandler(404)
def page_not_found(error):  # pragma: no cover
    """
    Custom 404 error
    """
    app.logger.debug("page_not_found: %s", error)
    resp = make_response('Page not found', 404)
    return resp


# Shutdown Web server ...
def shutdown_server():  # pragma: no cover
    """ ../.. """
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    # pragma: no cover - impossible to reach with unit testing ...
    func()


@app.route('/shutdown', methods=['POST'])
def shutdown():  # pragma: no cover
    """ ../.. """
    shutdown_server()
    return 'Server shutting down...'
