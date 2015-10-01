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
from flask import Flask, session, redirect, url_for, escape, request, render_template, flash, get_flashed_messages
import flask_login
from flask.ext.login import LoginManager, UserMixin, login_required, current_user, login_user, logout_user

from alignak_webui import app
from alignak_webui.user import User


@app.route('/')
@app.route('/index')
def index():
    """ ../.. """
    return (
        '''
            <h1>Hello {1}</h1>
            <p style="color: #f00;">{0}</p>
            <p><a href="/logout">Logout</a></p>
            <p><a href="/login">Login</a></p>
        '''.format(
            # flash message
            ', '.join([ str(m) for m in get_flashed_messages() ]),
            current_user.get_id() or 'Guest'
        )
    )

@app.route("/protected/",methods=["GET"])
@login_required
def protected():
    return Response(response="Hello Protected World!", status=200)



@app.route('/register' , methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    user = User(request.form['username'], request.form['password'], request.form['email'])
    # db.session.add(user)
    # db.session.commit()
    flash('User successfully registered')
    return redirect(url_for('login'))


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        app.logger.info("show login form ...")
        return render_template('login.html')

    username = request.form['username']
    password = request.form['password']
    app.logger.info("request authentication for: %s", username)
    user = User(username, password)
    login_user(user)
    flash('Logged in successfully.')
    next = request.args.get('next')

    return redirect(next or url_for('index'))
    return render_template('login.html', form=form)

@app.route('/login/check', methods=['post'])
def login_check():
    # validate username and password
    user = User.get(request.form['username'])
    if (user and user.password == request.form['password']):
        login_user(user)
    else:
        flash('Username or password incorrect')

    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


# Shutdown Web server ...
def shutdown_server():
    """ ../.. """
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@app.route('/shutdown', methods=['POST'])
def shutdown():
    """ ../.. """
    shutdown_server()
    return 'Server shutting down...'
