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
# import the unit testing module

import os
import unittest
import unittest

from nose import with_setup # optional
from nose.tools import *

import alignak_webui
from alignak_webui.backend import FrontEnd
from alignak_webui import app, frontend, manifest, settings
from alignak_webui.user import User
from alignak_webui.utils.settings import Settings
from alignak_webui.utils.helper import Helper

def setup_module(module):
    print ("") # this is to get a newline after the dots
    print ("setup_module before anything in this file")

def teardown_module(module):
    print ("") # this is to get a newline after the dots
    print ("teardown_module after everything in this file")



# extend the class unittest.TestCase
class basic_tests(unittest.TestCase):

    def setUp(self):
        print ""
        print "setting up ..."

        alignak_webui.app.config['HOST'] = '127.0.0.1'
        alignak_webui.app.config['PORT'] = 80
        alignak_webui.app.config['DEBUG'] = False

        alignak_webui.app.config['TESTING'] = True

        cfg_file = "settings.cfg"
        print 'Required configuration file:', cfg_file
        sett = Settings(alignak_webui.app)
        found_cfg_files = sett.read(cfg_file, {})
        if not found_cfg_files:
            print "Required configuration file not found."
            sys.exit(1)
        print 'Found configuration file:', cfg_file

        # Initialize backend communication ...
        frontend.configure(alignak_webui.app.config.get('ui.backend', 'http://localhost:5000'))
        print "Frontend: %s", frontend.url_endpoint_root

        # Configure users' management backend
        User.set_backend(frontend)

        self.app = alignak_webui.app.test_client()

    def tearDown(self):
        print ""
        print "tearing down ..."

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def test_2_login(self):
        print ''
        print 'test login/logout process'

        print 'get login page'
        rv = self.app.get('/login')
        assert '<form id="login"' in rv.data

        print 'login refused - credentials'
        rv = self.login('admin', 'default')
        assert 'Invalid credentials: username is unknown or password is invalid.' in rv.data

        print 'login refused - credentials'
        rv = self.login('admin', '')
        assert 'Invalid credentials: username is unknown or password is invalid.' in rv.data

        print 'login accepted - home page'
        rv = self.login('admin', 'admin')
        assert '<title>Home page</title>' in rv.data

        print 'refresh home page'
        rv = self.app.get('/')
        assert '<title>Home page</title>' in rv.data

        print 'logout - go to login page'
        rv = self.logout()
        assert '<form id="login"' in rv.data

    def test_3_shutdown(self):
        print ''
        print 'test server shutdown'

        with assert_raises(RuntimeError) as cm:
            rv = self.app.post('/shutdown')
            print rv.data
        ex = cm.exception # raised exception is available through exception property of context
        print 'exception:', str(ex)
        assert 'Not running with the Werkzeug Server' in str(ex)


if __name__ == '__main__':
    unittest.main()
