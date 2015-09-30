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

import unittest
import subprocess
import os, sys, signal
import time


from nose import with_setup # optional
from nose.tools import *

def setup_module(module):
    print " ... "
    print "setup_module before anything in this file"

def teardown_module(module):
    print " ... "
    print "teardown_module after everything in this file"


import alignak_webui
from alignak_webui import app, __application__, settings, __version__, __copyright__
from alignak_webui import __releasenotes__, __license__, __doc_url__, get_version

# extend the class unittest.TestCase
class test_config(unittest.TestCase):

    def test_1_manifest(self):
        print 'test config'

        print "application: %s" % __application__
        print "version: %s / %s" % (__version__, get_version())
        print "license: %s" % __license__
        print "copyright: %s" % __copyright__
        print "release: %s" % __releasenotes__
        print "doc: %s" % __doc_url__

    def test_2_start_usage(self):
        print ('test application start - show usage')

        mydir = os.getcwd()
        print
        print "Launching application ..."
        os.chdir("..")
        process = subprocess.Popen(['python', 'start.py', '-h'])
        print 'PID = ', process.pid
        time.sleep(3.0)
        print "Killing application ..."
        process.kill()
        os.chdir(mydir)
        # output = sys.stdout.getvalue().strip()
        # print output
        # ok_('Usage:' in output)
        # Output do not seem to be available because of process launch ...

    def test_2_start_version(self):
        print ('test application start - show version')

        mydir = os.getcwd()
        print
        print "Launching application ..."
        os.chdir("..")
        process = subprocess.Popen(['python', 'start.py', '--version'])
        print 'PID = ', process.pid
        time.sleep(3.0)
        print "Killing application ..."
        process.kill()
        os.chdir(mydir)

    def test_3_start_application(self):
        print ('test application start in normal mode (no logs)')

        mydir = os.getcwd()
        print
        print "Launching application ..."
        os.chdir("..")
        process = subprocess.Popen(['python', 'start.py', 'start'])
        print 'PID = ', process.pid
        time.sleep(3.0)
        print "Killing application ..."
        process.kill()
        os.chdir(mydir)

    def test_4_start_application_verbose(self):
        print ('test application start in verbose mode')

        mydir = os.getcwd()
        print
        print "Launching application ..."
        os.chdir("..")
        process = subprocess.Popen(['python', 'start.py', '-v', 'start'])
        print 'PID = ', process.pid
        time.sleep(3.0)
        print "Killing application ..."
        process.kill()
        os.chdir(mydir)

    def test_5_start_application_debug(self):
        print ('test application start in debug mode')

        mydir = os.getcwd()
        print
        print "Launching application ..."
        os.chdir("..")
        process = subprocess.Popen(['python', 'start.py', '-d', 'start'])
        print 'PID = ', process.pid
        time.sleep(3.0)
        print "Killing application ..."
        process.kill()
        os.chdir(mydir)

    def test_6_start_application_error(self):
        print ('test application start - error in application commande')

        mydir = os.getcwd()
        print
        print "Launching application ..."
        os.chdir("..")
        process = subprocess.Popen(['python', 'start.py', '-v', 'error'])
        print 'PID = ', process.pid
        time.sleep(3.0)
        print "Killing application ..."
        process.kill()
        os.chdir(mydir)

    def test_7_start_configuration_not_found(self):
        print ('test application start - configuration file not found')

        mydir = os.getcwd()
        print
        print "Launching application ..."
        os.chdir("..")
        process = subprocess.Popen(['python', 'start.py', '-v', '-c', 'test.cfg', 'start'])
        print 'PID = ', process.pid
        time.sleep(3.0)
        print "Killing application ..."
        process.kill()
        os.chdir(mydir)

    def test_8_start_configuration(self):
        print ('test application start - configuration file found')

        mydir = os.getcwd()
        print
        print "Launching application ..."
        os.chdir("..")
        process = subprocess.Popen(['python', 'start.py', '-v', '-c', 'settings.cfg', 'start'])
        print 'PID = ', process.pid
        time.sleep(3.0)
        print "Killing application ..."
        process.kill()
        os.chdir(mydir)
