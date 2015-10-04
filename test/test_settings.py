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


class settings_tests(unittest.TestCase):

    def setUp(self):
        print ""
        print "setting up ..."

    def tearDown(self):
        print ""
        print "tearing down ..."

        alignak_webui.app.config = {}


    def test_1_not_found(self):
        print ''
        print 'test login/logout process'

        # Relative file path
        cfg_file = "settings2.cfg"
        print 'Required configuration file:', cfg_file
        sett = Settings(alignak_webui.app)
        found_cfg_files = sett.read(cfg_file, {})
        print 'Found:', found_cfg_files
        self.assert_(found_cfg_files == None)

        # Absolute file path
        cfg_file = os.path.dirname(os.path.abspath(__file__)) + "/settings.cfg"
        print 'Required configuration file:', cfg_file
        sett = Settings(alignak_webui.app)
        found_cfg_files = sett.read(cfg_file, {})
        print 'Found:', found_cfg_files
        self.assert_(found_cfg_files == None)

        # Absolute file path - bad formed file
        cfg_file = os.path.dirname(os.path.abspath(__file__)) + "/test_settings.py"
        print 'Required configuration file:', cfg_file
        sett = Settings(alignak_webui.app)
        found_cfg_files = sett.read(cfg_file, {})
        print 'Found:', found_cfg_files
        self.assert_(found_cfg_files == None)

    def test_2_found(self):
        print ''

        # Relative file path
        cfg_file = "test_settings.cfg"
        print 'Required configuration file:', cfg_file
        sett = Settings(alignak_webui.app)
        found_cfg_files = sett.read(cfg_file, {})
        print 'Found:', found_cfg_files
        print alignak_webui.app.config
        self.assert_('HOST' in alignak_webui.app.config)
        self.assert_('PORT' in alignak_webui.app.config)
        self.assert_('SECRET_KEY' in alignak_webui.app.config)
        self.assert_(len(alignak_webui.app.config) > 10)
        self.assert_(found_cfg_files)

    def test_2_found_2(self):
        print ''

        # Absolute file path
        cfg_file = os.path.dirname(os.path.abspath(__file__)) + "/test_settings.cfg"
        print 'Required configuration file:', cfg_file
        sett = Settings(alignak_webui.app)
        found_cfg_files = sett.read(cfg_file, {})
        print 'Found:', found_cfg_files
        print alignak_webui.app.config
        self.assert_('HOST' in alignak_webui.app.config)
        self.assert_('PORT' in alignak_webui.app.config)
        self.assert_('SECRET_KEY' in alignak_webui.app.config)
        self.assert_(found_cfg_files)

    def test_2_found_3(self):
        print ''

        # Absolute file path - missing flask section
        cfg_file = os.path.dirname(os.path.abspath(__file__)) + "/test_settings2.cfg"
        print 'Required configuration file:', cfg_file
        sett = Settings(alignak_webui.app)
        found_cfg_files = sett.read(cfg_file, {})
        print 'Found:', found_cfg_files
        print alignak_webui.app.config
        self.assert_('HOST' in alignak_webui.app.config)
        self.assert_('PORT' in alignak_webui.app.config)
        self.assert_('SECRET_KEY' in alignak_webui.app.config)
        self.assert_(found_cfg_files)
