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

    def test_1_index(self):
        print ""
        print "get home page ..."

        rv = self.app.get('/')
        print rv.data
        assert 'You are not logged in' in rv.data

    def test_2_bad_secret(self):
        print ''
        print 'test secret key not set'

        with assert_raises(RuntimeError) as cm:
            rv = self.login('foo', 'foo')
        ex = cm.exception # raised exception is available through exception property of context
        print 'exception:', str(ex)
        assert 'the session is unavailable because no secret key was set.  Set the secret_key on the application to something unique and secret.' in str(ex)

        # Build a secret key if none defined ...
        if 'SECRET_KEY' not in alignak_webui.app.config or not alignak_webui.app.config['SECRET_KEY']:
            alignak_webui.app.config['SECRET_KEY'] = os.urandom(24)

    def test_3_login(self):
        print ''
        print 'test login/logout process'

        rv = self.app.get('/login')
        assert '<input type=text name=username>' in rv.data

        rv = self.login('admin', 'default')
        assert 'Logged in as admin' in rv.data

        rv = self.logout()
        assert 'You are not logged in' in rv.data


if __name__ == '__main__':
    unittest.main()
