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
User login / management
"""
from flask import redirect, url_for, request, render_template, flash

from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from flask_login import current_user
from alignak_webui.backend import FrontEnd
from alignak_webui import app, frontend, manifest, settings
from alignak_webui.user import User

# Login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.token_loader
def token_loader(token):  # pragma: no cover - very difficult with unit testing ...
    """
    Called when user login check is required
    """
    # pragma: no cover - very difficult with unit testing ...
    app.logger.debug("token_loader - Try to find user with token: %s", token)
    return User.get_from_token(token)


@login_manager.user_loader
def user_loader(user_id):
    """
    Called when user login check is required
    """
    app.logger.debug("user_loader - Try to find user with token: %s", user_id)
    return User.get_from_username(user_id)


@login_manager.request_loader
def request_loader(req):
    """
    Called when user login check is required
    """
    app.logger.debug("request_loader - Try to find user from request: %s", req)
    token = req.headers.get('Authorization')
    if token is None:
        token = req.args.get('token')

    if token is not None:  # pragma: no cover - very difficult with unit testing ...
        app.logger.debug("load_user - found user token in request")
        return User.get_from_token(token)
    return None


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login ...

    If GET request, display login form
    If POST request, authenticates user and redirects to index page
    """
    # Get configured backend ...
    # frontend = app.config['frontend']

    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        app.logger.info("login request for: %s", username)

        user = User()
        if user.authenticate(username, password):
            if login_user(user, remember=True):
                # Initialize backend
                flash(u"You were successfully logged in.", 'info')
                return redirect(request.args.get('next') or url_for('index'))
            else:  # pragma: no cover - should never happen ...
                error = u"User login failed."
        else:
            error = u"Invalid credentials: username is unknown or password is invalid."

    app.logger.info("show login form ...")
    return render_template(
        'login.html',
        error=error,
        title=u"Login page",
        manifest=manifest
    )


@app.route('/logout')
def logout():
    """
    User logout ... simply logout current user and redirects to index page
    """
    logout_user()
    return redirect(url_for('index'))
