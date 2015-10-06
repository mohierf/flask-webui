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
from subprocess import CalledProcessError
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
from alignak_webui import app, frontend, manifest, settings
from alignak_webui import __application__, __version__, __copyright__
from alignak_webui import __releasenotes__, __license__, __doc_url__
from alignak_webui.utils.plugins import Plugins

class test_1_run(unittest.TestCase):

    def test_1_manifest(self):
        print 'test config'

        print "application: %s" % __application__
        print "version: %s" % __version__
        print "license: %s" % __license__
        print "copyright: %s" % __copyright__
        print "release: %s" % __releasenotes__
        print "doc: %s" % __doc_url__

    def test1_plugins(self):
        # Application current directory, find plugins directory ...
        app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))

        # Load application plugins
        plugins = Plugins(app)
        plugins_dir = os.path.join(
            os.path.join(app_dir, manifest['name'].lower()),
            app.config.get('ui.plugins_dir', 'plugins')
        )
        nb_plugins = plugins.load_plugins(plugins_dir)
        assert nb_plugins > 0

    def test_2_start_usage(self):
        print ('test application start - show usage')

        mydir = os.getcwd()
        print
        print "Launching application ..."
        os.chdir("..")
        output = subprocess.check_output(['python', 'app.py', '-h'])
        os.chdir(mydir)
        assert '{command} [-h] [-d|-v] [-c=cfg_file] [-l=logs_file] [-a=access_log] <command>' in output
        # output = sys.stdout.getvalue().strip()
        # print output
        # ok_('Usage:' in output)
        # Output do not seem to be available because of process launch ...

    def test_3_start_version(self):
        print ('test application start - show version')

        mydir = os.getcwd()
        print
        print "Launching application ..."
        os.chdir("..")
        output = subprocess.check_output(['python', 'app.py', '--version'])
        print output
        os.chdir(mydir)

    def test_4_start_bad_argument(self):
        print ('test application start - bad argument')

        mydir = os.getcwd()
        print
        print "Launching application ..."
        os.chdir("..")
        with assert_raises(CalledProcessError) as cm:
            process = subprocess.check_call(['python', 'app.py', '--error'])
        ex = cm.exception # raised exception is available through exception property of context
        print 'exception:', str(ex)
        assert 'returned non-zero exit status 1' in str(ex)
        os.chdir(mydir)

    def test_5_start_application_error(self):
        print ('test application start - error in application commande')

        mydir = os.getcwd()
        print
        print "Launching application ..."
        os.chdir("..")
        # with assert_raises(CalledProcessError) as cm:
        output = subprocess.check_call(['python', 'app.py', '-v', 'error'])
        # ex = cm.exception
        # print 'exception:', str(ex)
        # assert 'returned non-zero exit status 1' in str(ex)
        os.chdir(mydir)

    def test_6_start_configuration_not_found(self):
        print ('test application start - configuration file not found')

        mydir = os.getcwd()
        print
        print "Launching application ..."
        os.chdir("..")
        with assert_raises(CalledProcessError) as cm:
            output = subprocess.check_call(['python', 'app.py', '-v', '-c', 'test.cfg', 'start'])
        ex = cm.exception
        print 'exception:', str(ex)
        assert 'returned non-zero exit status 1' in str(ex)
        os.chdir(mydir)


class test_2_server(unittest.TestCase):

    def test_1_start_application(self):
        print ('test application start in normal mode (no logs)')

        mydir = os.getcwd()
        print
        print "Launching application ..."
        os.chdir("..")
        process = subprocess.Popen(['python', 'app.py', 'start'])
        print 'PID = ', process.pid
        time.sleep(2.0)
        print "Killing application ..."
        # Application starts with default configuration (debug=False)
        # If debut is True 2 processes are started and the 2nd process can not be killed !
        process.terminate()
        os.chdir(mydir)

    def test_2_start_application_verbose(self):
        print ('test application start in verbose mode')

        mydir = os.getcwd()
        print
        print "Launching application ..."
        os.chdir("..")
        process = subprocess.Popen(['python', 'app.py', '-v', 'start'])
        print 'PID = ', process.pid
        time.sleep(3.0)
        print "Killing application ..."
        process.terminate()
        os.chdir(mydir)

    def test_3_start_application_debug(self):
        print ('test application start in debug mode')

        mydir = os.getcwd()
        print
        print "Launching application ..."
        os.chdir("..")
        process = subprocess.Popen(['python', 'app.py', '-d', 'start'])
        print 'PID = ', process.pid
        time.sleep(3.0)
        print "Killing application ..."
        process.terminate()
        os.chdir(mydir)

    def test_4_start_configuration(self):
        print ('test application start - configuration file found')

        mydir = os.getcwd()
        print
        print "Launching application ..."
        os.chdir("..")
        process = subprocess.Popen(['python', 'app.py', '-v', '-c', 'settings.cfg', 'start'])
        print 'PID = ', process.pid
        time.sleep(3.0)
        print "Killing application ..."
        process.terminate()
        os.chdir(mydir)


if __name__ == '__main__':
    unittest.main()
