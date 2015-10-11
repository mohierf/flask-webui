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
import time
import unittest

from nose import with_setup # optional
from nose.tools import *

def setup_module(module):
    print ("") # this is to get a newline after the dots
    print ("setup_module before anything in this file")

def teardown_module(module):
    print ("") # this is to get a newline after the dots
    print ("teardown_module after everything in this file")

import alignak_webui
from alignak_webui import app, frontend, manifest, settings
from alignak_webui.user import User
from alignak_webui.utils.settings import Settings
from alignak_webui.utils.helper import Helper
from flask_login import current_user

# extend the class unittest.TestCase
class test_helper(unittest.TestCase):

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

        self.helper = Helper(alignak_webui.app)

    def tearDown(self):
        print ""
        print "tearing down ..."


    def test_01_print_date(self):
        print "---"

        now = time.time()

        # Timestamp errors
        s = self.helper.print_date(None)
        print "Result:", s
        self.assert_(s == 'n/a')

        s = self.helper.print_date(0)
        print "Result:", s
        self.assert_(s == 'n/a')

        # Now, default format
        s = self.helper.print_date(now)
        print "Result:", s

        # Now, specified format
        s = self.helper.print_date(now, fmt='%Y-%m-%d')
        print "Result:", s

        s = self.helper.print_date(now, fmt='%H:%M:%S')
        print "Result:", s

    def test_02_print_duration(self):
        print "---"

        now = time.time()

        # Timestamp errors
        s = self.helper.print_duration(None)
        print "Result:", s
        self.assert_(s == 'n/a')
        s = self.helper.print_duration(0)
        print "Result:", s
        self.assert_(s == 'n/a')

        # Now, default format
        s = self.helper.print_duration(now)
        print "Result:", s
        self.assert_(s == 'Now')

        # In the past ...
        # 2s ago
        s = self.helper.print_duration(now - 2)
        print "Result:", s
        self.assert_(s == '2s ago')

        # Only the duration string
        s = self.helper.print_duration(now - 2, duration_only=True)
        print "Result:", s
        self.assert_(s == '2s')

        # Got 2minutes
        s = self.helper.print_duration(now - 120)
        print "Result:", s
        self.assert_(s == '2m ago')

        # Go 2hours ago
        s = self.helper.print_duration(now - 3600*2)
        print "Result:", s
        self.assert_(s == '2h ago')

        # Go 2 days ago
        s = self.helper.print_duration(now - 3600*24*2)
        print "Result:", s
        self.assert_(s == '2d ago')

        # Go 2 weeks ago
        s = self.helper.print_duration(now - 86400*14)
        print "Result:", s
        self.assert_(s == '2w ago')

        # Go 2 months ago
        s = self.helper.print_duration(now - 86400*56)
        print "Result:", s
        self.assert_(s == '2M ago')

        # Go 1 year ago
        s = self.helper.print_duration(now - 86400*365*2)
        print "Result:", s
        self.assert_(s == '2y ago')

        # Now a mix of all of this :)
        s = self.helper.print_duration(now - 2 - 120 - 3600*2 - 3600*24*2 - 86400*14 - 86400*56)
        print "Result:", s
        self.assert_(s == '2M 2w 2d 2h 2m 2s ago')

        # Now with a limit, because here it's just a nightmare to read
        s = self.helper.print_duration(now - 2 - 120 - 3600*2 - 3600*24*2 - 86400*14 - 86400*56, x_elts=2)
        print "Result:", s
        self.assert_(s == '2M 2w ago')

        # Return to the future
        # Get the 2s ago
        s = self.helper.print_duration(now + 2)
        print "Result:", s
        self.assert_(s == 'in 2s')

        # Got 2minutes
        s = self.helper.print_duration(now + 120)
        print "Result:", s
        self.assert_(s == 'in 2m')

        # Go 2hours ago
        s = self.helper.print_duration(now + 3600*2)
        print "Result:", s
        self.assert_(s == 'in 2h')

        # Go 2 days ago
        s = self.helper.print_duration(now + 3600*24*2)
        print "Result:", s
        self.assert_(s == 'in 2d')

        # Go 2 weeks ago
        s = self.helper.print_duration(now + 86400*14)
        print "Result:", s
        self.assert_(s == 'in 2w')

        # Go 2 months ago
        s = self.helper.print_duration(now + 86400*56)
        print "Result:", s
        self.assert_(s == 'in 2M')

        # Go 1 year ago
        s = self.helper.print_duration(now + 86400*365*2)
        print "Result:", s
        self.assert_(s == 'in 2y')

        # Now a mix of all of this :)
        s = self.helper.print_duration(now + 2 + 120 + 3600*2 + 3600*24*2 + 86400*14 + 86400*56)
        print "Result:", s
        self.assert_(s == 'in 2M 2w 2d 2h 2m 2s')

        # Now with a limit, because here it's just a nightmare to read
        s = self.helper.print_duration(now + 2 - 120 + 3600*2 + 3600*24*2 + 86400*14 + 86400*56, x_elts=2)
        print "Result:", s
        self.assert_(s == 'in 2M 2w')

    def test_03_get_business_impact_text(self):
        print "---"

        # Parameters errors
        s = self.helper.get_html_business_impact(10)
        print "Result:", s
        self.assert_(s == 'n/a')

        s = self.helper.get_html_business_impact(6, text=False)
        print "Result:", s
        self.assert_(s == 'n/a')

        s = self.helper.get_html_business_impact(-1)
        print "Result:", s
        self.assert_(s == 'n/a')

        s = self.helper.get_html_business_impact(1, False, False)
        print "Result:", s
        self.assert_(s == 'n/a')

        s = self.helper.get_html_business_impact(1, text=False, icon=False)
        print "Result:", s
        self.assert_(s == 'n/a')

        # Default ... text and stars
        s = self.helper.get_html_business_impact(0)
        print "Result:", s
        self.assert_(s == 'None')
        s = self.helper.get_html_business_impact(1)
        print "Result:", s
        self.assert_(s == 'Low')
        s = self.helper.get_html_business_impact(2)
        print "Result:", s
        self.assert_(s == 'Normal')
        s = self.helper.get_html_business_impact(3)
        print "Result:", s
        self.assert_(s == 'Important <i class="fa fa-star text-primary"></i>')
        s = self.helper.get_html_business_impact(4)
        print "Result:", s
        self.assert_(s == 'Very important <i class="fa fa-star text-primary"></i><i class="fa fa-star text-primary"></i>')
        s = self.helper.get_html_business_impact(5)
        print "Result:", s
        self.assert_(s == 'Business critical <i class="fa fa-star text-primary"></i><i class="fa fa-star text-primary"></i><i class="fa fa-star text-primary"></i>')

        # Stars only ...
        s = self.helper.get_html_business_impact(0, text=False)
        print "Result:", s
        self.assert_(s == '')
        s = self.helper.get_html_business_impact(1, text=False)
        print "Result:", s
        self.assert_(s == '')
        s = self.helper.get_html_business_impact(2, text=False)
        print "Result:", s
        self.assert_(s == '')
        s = self.helper.get_html_business_impact(3, text=False)
        print "Result:", s
        self.assert_(s == '<i class="fa fa-star text-primary"></i>')
        s = self.helper.get_html_business_impact(4, text=False)
        print "Result:", s
        self.assert_(s == '<i class="fa fa-star text-primary"></i><i class="fa fa-star text-primary"></i>')
        s = self.helper.get_html_business_impact(5, text=False)
        print "Result:", s
        self.assert_(s == '<i class="fa fa-star text-primary"></i><i class="fa fa-star text-primary"></i><i class="fa fa-star text-primary"></i>')

        # Text only ...
        s = self.helper.get_html_business_impact(0, icon=False)
        print "Result:", s
        self.assert_(s == 'None')
        s = self.helper.get_html_business_impact(1, icon=False)
        print "Result:", s
        self.assert_(s == 'Low')
        s = self.helper.get_html_business_impact(2, icon=False)
        print "Result:", s
        self.assert_(s == 'Normal')
        s = self.helper.get_html_business_impact(3, icon=False)
        print "Result:", s
        self.assert_(s == 'Important')
        s = self.helper.get_html_business_impact(4, icon=False)
        print "Result:", s
        self.assert_(s == 'Very important')
        s = self.helper.get_html_business_impact(5, icon=False)

    def test_04_get_state_text(self):
        print "---"

        print "Parameters errors:"
        s = self.helper.get_html_state('', '')
        print "Result:", s
        self.assert_(s == 'n/a')

        s = self.helper.get_html_state('host', 'bad state')
        print "Result:", s
        self.assert_(s == 'n/a')

        s = self.helper.get_html_state('service', 'bad state')
        print "Result:", s
        self.assert_(s == 'n/a')

        s = self.helper.get_html_state('host', 'UP', extra='bad state')
        print "Result:", s
        self.assert_(s == 'n/a')

        s = self.helper.get_html_state('service', 'OK', extra='bad state')
        print "Result:", s
        self.assert_(s == 'n/a')

        s = self.helper.get_html_state('host', 'UP', icon=False, text=False)
        print "Result:", s
        self.assert_(s == 'n/a')

        s = self.helper.get_html_state('service', 'OK', icon=False, text=False)
        print "Result:", s
        self.assert_(s == 'n/a')

    def test_05_get_host_state_text(self):
        print "---"

        # Host, icon only (default) ...
        s = self.helper.get_html_state('host', 'UP')
        print "Result:", s
        self.assert_(s == '<center class="font-up"><span class="fa-stack" title="host state is UP"><i class="fa fa-circle fa-stack-2x font-up"></i><i class="fa fa-server fa-stack-1x fa-inverse"></i></span><div></div></center>')
        s = self.helper.get_html_state('host', 'DOWN')
        print "Result:", s
        self.assert_(s == '<center class="font-down"><span class="fa-stack" title="host state is DOWN"><i class="fa fa-circle fa-stack-2x font-down"></i><i class="fa fa-server fa-stack-1x fa-inverse"></i></span><div></div></center>')
        s = self.helper.get_html_state('host', 'UNREACHABLE')
        print "Result:", s
        self.assert_(s == '<center class="font-unreachable"><span class="fa-stack" title="host state is UNREACHABLE"><i class="fa fa-circle fa-stack-2x font-unreachable"></i><i class="fa fa-server fa-stack-1x fa-inverse"></i></span><div></div></center>')
        s = self.helper.get_html_state('host', 'UP', extra='FLAPPING')
        print "Result:", s
        self.assert_(s == '<center class="font-up"><span class="fa-stack" title="host state is UP and flapping"><i class="fa fa-circle fa-stack-2x font-up"></i><i class="fa fa-server fa-stack-1x font-up"></i></span><div></div></center>')
        s = self.helper.get_html_state('host', 'DOWN', extra='FLAPPING')
        print "Result:", s
        self.assert_(s == '<center class="font-down"><span class="fa-stack" title="host state is DOWN and flapping"><i class="fa fa-circle fa-stack-2x font-down"></i><i class="fa fa-server fa-stack-1x font-down"></i></span><div></div></center>')
        s = self.helper.get_html_state('host', 'DOWN', extra='ACKNOWLEDGED')
        print "Result:", s
        self.assert_(s == '<center class="font-down"><span class="fa-stack" style="opacity: 0.5" title="host state is DOWN and acknowledged"><i class="fa fa-circle fa-stack-2x font-down"></i><i class="fa fa-server fa-stack-1x fa-inverse"></i></span><div></div></center>')
        s = self.helper.get_html_state('host', 'DOWN', extra='IN_DOWNTIME')
        print "Result:", s
        self.assert_(s == '<center class="font-down"><span class="fa-stack" style="opacity: 0.5" title="host state is DOWN but downtime is scheduled"><i class="fa fa-circle fa-stack-2x font-down"></i><i class="fa fa-server fa-stack-1x fa-inverse"></i></span><div></div></center>')
        # Host, text only ...
        s = self.helper.get_html_state('host', 'UP', text=True, icon=False)
        print "Result:", s
        self.assert_(s == 'host state is UP')
        s = self.helper.get_html_state('host', 'DOWN', text=True, icon=False)
        print "Result:", s
        self.assert_(s == 'host state is DOWN')
        s = self.helper.get_html_state('host', 'UNREACHABLE', text=True, icon=False)
        print "Result:", s
        self.assert_(s == 'host state is UNREACHABLE')
        s = self.helper.get_html_state('host', 'UP', extra='FLAPPING', text=True, icon=False)
        print "Result:", s
        self.assert_(s == 'host state is UP and flapping')
        s = self.helper.get_html_state('host', 'DOWN', extra='FLAPPING', text=True, icon=False)
        print "Result:", s
        self.assert_(s == 'host state is DOWN and flapping')
        s = self.helper.get_html_state('host', 'DOWN', extra='ACKNOWLEDGED', text=True, icon=False)
        print "Result:", s
        self.assert_(s == 'host state is DOWN and acknowledged')
        s = self.helper.get_html_state('host', 'DOWN', extra='IN_DOWNTIME', text=True, icon=False)
        print "Result:", s
        self.assert_(s == 'host state is DOWN but downtime is scheduled')

        # Host, icon and text ...
        s = self.helper.get_html_state('host', 'UP', text=True, icon=True)
        print "Result:", s
        self.assert_(s == '<center class="font-up"><span class="fa-stack" title="host state is UP"><i class="fa fa-circle fa-stack-2x font-up"></i><i class="fa fa-server fa-stack-1x fa-inverse"></i></span><div>host state is UP</div></center>')
        s = self.helper.get_html_state('host', 'DOWN', text=True, icon=True)
        print "Result:", s
        self.assert_(s == '<center class="font-down"><span class="fa-stack" title="host state is DOWN"><i class="fa fa-circle fa-stack-2x font-down"></i><i class="fa fa-server fa-stack-1x fa-inverse"></i></span><div>host state is DOWN</div></center>')
        s = self.helper.get_html_state('host', 'UNREACHABLE', text=True, icon=True)
        print "Result:", s
        self.assert_(s == '<center class="font-unreachable"><span class="fa-stack" title="host state is UNREACHABLE"><i class="fa fa-circle fa-stack-2x font-unreachable"></i><i class="fa fa-server fa-stack-1x fa-inverse"></i></span><div>host state is UNREACHABLE</div></center>')
        s = self.helper.get_html_state('host', 'UP', extra='FLAPPING', text=True, icon=True)
        print "Result:", s
        self.assert_(s == '<center class="font-up"><span class="fa-stack" title="host state is UP and flapping"><i class="fa fa-circle fa-stack-2x font-up"></i><i class="fa fa-server fa-stack-1x font-up"></i></span><div>host state is UP and flapping</div></center>')
        s = self.helper.get_html_state('host', 'DOWN', extra='FLAPPING', text=True, icon=True)
        print "Result:", s
        self.assert_(s == '<center class="font-down"><span class="fa-stack" title="host state is DOWN and flapping"><i class="fa fa-circle fa-stack-2x font-down"></i><i class="fa fa-server fa-stack-1x font-down"></i></span><div>host state is DOWN and flapping</div></center>')
        s = self.helper.get_html_state('host', 'DOWN', extra='ACKNOWLEDGED', text=True, icon=True)
        print "Result:", s
        self.assert_(s == '<center class="font-down"><span class="fa-stack" style="opacity: 0.5" title="host state is DOWN and acknowledged"><i class="fa fa-circle fa-stack-2x font-down"></i><i class="fa fa-server fa-stack-1x fa-inverse"></i></span><div>host state is DOWN and acknowledged</div></center>')
        s = self.helper.get_html_state('host', 'DOWN', extra='IN_DOWNTIME', text=True, icon=True)
        print "Result:", s
        self.assert_(s == '<center class="font-down"><span class="fa-stack" style="opacity: 0.5" title="host state is DOWN but downtime is scheduled"><i class="fa fa-circle fa-stack-2x font-down"></i><i class="fa fa-server fa-stack-1x fa-inverse"></i></span><div>host state is DOWN but downtime is scheduled</div></center>')

    def test_06_get_service_state_text(self):
        print "---"

        # service, icon only (default) ...
        s = self.helper.get_html_state('service', 'OK')
        print "Result:", s
        self.assert_(s == '<center class="font-ok"><span class="fa-stack" title="service state is OK"><i class="fa fa-circle fa-stack-2x font-ok"></i><i class="fa fa-arrow-up fa-stack-1x fa-inverse"></i></span><div></div></center>')
        s = self.helper.get_html_state('service', 'CRITICAL')
        print "Result:", s
        self.assert_(s == '<center class="font-critical"><span class="fa-stack" title="service state is CRITICAL"><i class="fa fa-circle fa-stack-2x font-critical"></i><i class="fa fa-arrow-down fa-stack-1x fa-inverse"></i></span><div></div></center>')
        s = self.helper.get_html_state('service', 'WARNING')
        print "Result:", s
        self.assert_(s == '<center class="font-warning"><span class="fa-stack" title="service state is WARNING"><i class="fa fa-circle fa-stack-2x font-warning"></i><i class="fa fa-exclamation fa-stack-1x fa-inverse"></i></span><div></div></center>')
        s = self.helper.get_html_state('service', 'UNKNOWN')
        print "Result:", s
        self.assert_(s == '<center class="font-unknown"><span class="fa-stack" title="service state is UNKNOWN"><i class="fa fa-circle fa-stack-2x font-unknown"></i><i class="fa fa-question fa-stack-1x fa-inverse"></i></span><div></div></center>')
        s = self.helper.get_html_state('service', 'ok', extra='FLAPPING')
        print "Result:", s
        self.assert_(s == '<center class="font-ok"><span class="fa-stack" title="service state is OK and flapping"><i class="fa fa-circle fa-stack-2x font-ok"></i><i class="fa fa-arrow-up fa-stack-1x font-ok"></i></span><div></div></center>')
        s = self.helper.get_html_state('service', 'CRITICAL', extra='FLAPPING')
        print "Result:", s
        self.assert_(s == '<center class="font-critical"><span class="fa-stack" title="service state is CRITICAL and flapping"><i class="fa fa-circle fa-stack-2x font-critical"></i><i class="fa fa-arrow-down fa-stack-1x font-critical"></i></span><div></div></center>')
        s = self.helper.get_html_state('service', 'CRITICAL', extra='ACKNOWLEDGED')
        print "Result:", s
        self.assert_(s == '<center class="font-critical"><span class="fa-stack" style="opacity: 0.5" title="service state is CRITICAL and acknowledged"><i class="fa fa-circle fa-stack-2x font-critical"></i><i class="fa fa-arrow-down fa-stack-1x fa-inverse"></i></span><div></div></center>')
        s = self.helper.get_html_state('service', 'CRITICAL', extra='IN_DOWNTIME')
        print "Result:", s
        self.assert_(s == '<center class="font-critical"><span class="fa-stack" style="opacity: 0.5" title="service state is CRITICAL but downtime is scheduled"><i class="fa fa-circle fa-stack-2x font-critical"></i><i class="fa fa-arrow-down fa-stack-1x fa-inverse"></i></span><div></div></center>')

        # service, text only ...
        s = self.helper.get_html_state('service', 'OK', text=True, icon=False)
        print "Result:", s
        self.assert_(s == 'service state is OK')
        s = self.helper.get_html_state('service', 'CRITICAL', text=True, icon=False)
        print "Result:", s
        self.assert_(s == 'service state is CRITICAL')
        s = self.helper.get_html_state('service', 'WARNING', text=True, icon=False)
        print "Result:", s
        self.assert_(s == 'service state is WARNING')
        s = self.helper.get_html_state('service', 'UNKNOWN', text=True, icon=False)
        print "Result:", s
        self.assert_(s == 'service state is UNKNOWN')
        s = self.helper.get_html_state('service', 'OK', extra='FLAPPING', text=True, icon=False)
        print "Result:", s
        self.assert_(s == 'service state is OK and flapping')
        s = self.helper.get_html_state('service', 'CRITICAL', extra='FLAPPING', text=True, icon=False)
        print "Result:", s
        self.assert_(s == 'service state is CRITICAL and flapping')
        s = self.helper.get_html_state('service', 'CRITICAL', extra='ACKNOWLEDGED', text=True, icon=False)
        print "Result:", s
        self.assert_(s == 'service state is CRITICAL and acknowledged')
        s = self.helper.get_html_state('service', 'CRITICAL', extra='IN_DOWNTIME', text=True, icon=False)
        print "Result:", s
        self.assert_(s == 'service state is CRITICAL but downtime is scheduled')

        # service, icon and text ...
        s = self.helper.get_html_state('service', 'OK', text=True, icon=True)
        print "Result:", s
        self.assert_(s == '<center class="font-ok"><span class="fa-stack" title="service state is OK"><i class="fa fa-circle fa-stack-2x font-ok"></i><i class="fa fa-arrow-up fa-stack-1x fa-inverse"></i></span><div>service state is OK</div></center>')
        s = self.helper.get_html_state('service', 'CRITICAL', text=True, icon=True)
        print "Result:", s
        self.assert_(s == '<center class="font-critical"><span class="fa-stack" title="service state is CRITICAL"><i class="fa fa-circle fa-stack-2x font-critical"></i><i class="fa fa-arrow-down fa-stack-1x fa-inverse"></i></span><div>service state is CRITICAL</div></center>')
        s = self.helper.get_html_state('service', 'WARNING', text=True, icon=True)
        print "Result:", s
        self.assert_(s == '<center class="font-warning"><span class="fa-stack" title="service state is WARNING"><i class="fa fa-circle fa-stack-2x font-warning"></i><i class="fa fa-exclamation fa-stack-1x fa-inverse"></i></span><div>service state is WARNING</div></center>')
        s = self.helper.get_html_state('service', 'UNKNOWN', text=True, icon=True)
        print "Result:", s
        self.assert_(s == '<center class="font-unknown"><span class="fa-stack" title="service state is UNKNOWN"><i class="fa fa-circle fa-stack-2x font-unknown"></i><i class="fa fa-question fa-stack-1x fa-inverse"></i></span><div>service state is UNKNOWN</div></center>')
        s = self.helper.get_html_state('service', 'ok', extra='FLAPPING', text=True, icon=True)
        print "Result:", s
        self.assert_(s == '<center class="font-ok"><span class="fa-stack" title="service state is OK and flapping"><i class="fa fa-circle fa-stack-2x font-ok"></i><i class="fa fa-arrow-up fa-stack-1x font-ok"></i></span><div>service state is OK and flapping</div></center>')
        s = self.helper.get_html_state('service', 'CRITICAL', extra='FLAPPING', text=True, icon=True)
        print "Result:", s
        self.assert_(s == '<center class="font-critical"><span class="fa-stack" title="service state is CRITICAL and flapping"><i class="fa fa-circle fa-stack-2x font-critical"></i><i class="fa fa-arrow-down fa-stack-1x font-critical"></i></span><div>service state is CRITICAL and flapping</div></center>')
        s = self.helper.get_html_state('service', 'CRITICAL', extra='ACKNOWLEDGED', text=True, icon=True)
        print "Result:", s
        self.assert_(s == '<center class="font-critical"><span class="fa-stack" style="opacity: 0.5" title="service state is CRITICAL and acknowledged"><i class="fa fa-circle fa-stack-2x font-critical"></i><i class="fa fa-arrow-down fa-stack-1x fa-inverse"></i></span><div>service state is CRITICAL and acknowledged</div></center>')
        s = self.helper.get_html_state('service', 'CRITICAL', extra='IN_DOWNTIME', text=True, icon=True)
        print "Result:", s
        self.assert_(s == '<center class="font-critical"><span class="fa-stack" style="opacity: 0.5" title="service state is CRITICAL but downtime is scheduled"><i class="fa fa-circle fa-stack-2x font-critical"></i><i class="fa fa-arrow-down fa-stack-1x fa-inverse"></i></span><div>service state is CRITICAL but downtime is scheduled</div></center>')

        # Use label instead of built text ...
        s = self.helper.get_html_state('service', 'OK', text=True, icon=True, label='My own label')
        print "Result:", s
        self.assert_(s == '<center class="font-ok"><span class="fa-stack" title="service state is OK"><i class="fa fa-circle fa-stack-2x font-ok"></i><i class="fa fa-arrow-up fa-stack-1x fa-inverse"></i></span><div>My own label</div></center>')

        # Specify disabled state ...
        s = self.helper.get_html_state('service', 'OK', text=True, icon=True, label='My own label', disabled=True)
        print "Result:", s
        self.assert_(s == '<center class="font-ok"><span class="fa-stack" title="service state is OK"><i class="fa fa-circle fa-stack-2x font-greyed"></i><i class="fa fa-arrow-up fa-stack-1x fa-inverse"></i></span><div>My own label</div></center>')

    def test_07_get_url(self):
        print "---"

        print "Parameters errors:"
        s = self.helper.get_html_url(None, None)
        print "Result:", s
        self.assert_(s == 'n/a')

        s = self.helper.get_html_url('', '')
        print "Result:", s
        self.assert_(s == 'n/a')

        s = self.helper.get_html_url('host', None)
        print "Result:", s
        self.assert_(s == 'n/a')

        s = self.helper.get_html_url('bad_type', 'bad')
        print "Result:", s
        self.assert_(s == '<a href="/bad_type/bad" title="bad">bad</a>')

        s = self.helper.get_html_url('host', 'host1')
        print "Result:", s
        self.assert_(s == '<a href="/host/host1" title="host1">host1</a>')

        s = self.helper.get_html_url('service', 'service1')
        print "Result:", s
        self.assert_(s == '<a href="/service/service1" title="service1">service1</a>')

        s = self.helper.get_html_url('host', 'test', 'My label ...')
        print "Result:", s
        self.assert_(s == '<a href="/host/test" title="test">My label ...</a>')

        s = self.helper.get_html_url('contact', 'bob', 'My label ...')
        print "Result:", s
        self.assert_(s == '<a href="/contact/bob" title="bob">My label ...</a>')

    def test_08_get_id(self):
        print "---"

        print "Parameters errors:"
        s = self.helper.get_html_id(None, None)
        print "Result:", s
        self.assert_(s == 'n/a')

        s = self.helper.get_html_id('', '')
        print "Result:", s
        self.assert_(s == 'n/a')

        s = self.helper.get_html_id('host', None)
        print "Result:", s
        self.assert_(s == 'n/a')

        s = self.helper.get_html_id('bad_type', 'bad')
        print "Result:", s
        self.assert_(s == 'bad_type-bad')

        s = self.helper.get_html_id('host', 'host1')
        print "Result:", s
        self.assert_(s == 'host-host1')

        s = self.helper.get_html_id('service', 'service1')
        print "Result:", s
        self.assert_(s == 'service-service1')

        s = self.helper.get_html_id('host', 'test*/-_+)')
        print "Result:", s
        self.assert_(s == 'host-test-_')

    def test_09_search(self):
        print "---"

        # Initialize backend communication ...
        frontend.configure(alignak_webui.app.config.get('ui.backend', 'http://localhost:5000'))
        print "Frontend: %s", frontend.url_endpoint_root

        # Configure users' management backend
        User.set_backend(frontend)

        # Force authentication ...
        connection = frontend.login('admin', 'admin', force=True)
        assert_true(frontend.authenticated)
        assert_true(frontend.token)

        connection = frontend.connect(username='admin')
        assert_true(frontend.authenticated)
        assert_true(frontend.connected)

        ls = self.helper.get_livestate()

        print "Search on element type ..."
        search = self.helper.search_livestate(ls, "type:all")
        print "Result, found %d elements" % len(search)
        search = self.helper.search_livestate(ls, "type:host")
        print "Result, found %d elements" % len(search)
        search = self.helper.search_livestate(ls, "type:service")
        print "Result, found %d elements" % len(search)
        search = self.helper.search_livestate(ls, "host")
        print "Result, found %d elements" % len(search)
        search = self.helper.search_livestate(ls, "service")
        print "Result, found %d elements" % len(search)
        search = self.helper.search_livestate(ls, "type:unknown")
        print "Result, found %d elements" % len(search)

        print "---"
        print "Search on element name and content ... "
        print "found in name ..."
        search = self.helper.search_livestate(ls, "charnay")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        print "found in output ..."
        search = self.helper.search_livestate(ls, "time")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        print "not found ..."
        search = self.helper.search_livestate(ls, "test")
        print "Result, found %d elements" % len(search)

        print "---"
        print "Search on element business impact ... "
        search = self.helper.search_livestate(ls, "bi:0")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_livestate(ls, "bi:=0")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_livestate(ls, "bi:>0")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_livestate(ls, "bi:>=0")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_livestate(ls, "bi:<5")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_livestate(ls, "bi:<=5")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_livestate(ls, "bi:>3")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0

        print "---"
        print "Search on element state ... "
        search = self.helper.search_livestate(ls, "is:ack")
        print "Result, found %d elements" % len(search)
        search = self.helper.search_livestate(ls, "ack:true")
        print "Result, found %d elements" % len(search)
        search = self.helper.search_livestate(ls, "ack:yes")
        print "Result, found %d elements" % len(search)
        search = self.helper.search_livestate(ls, "ack:1")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_livestate(ls, "isnot:ack")
        print "Result, found %d elements" % len(search)
        search = self.helper.search_livestate(ls, "ack:false")
        print "Result, found %d elements" % len(search)
        search = self.helper.search_livestate(ls, "ack:no")
        print "Result, found %d elements" % len(search)
        search = self.helper.search_livestate(ls, "ack:0")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_livestate(ls, "is:downtime")
        print "Result, found %d elements" % len(search)
        search = self.helper.search_livestate(ls, "downtime:yes")
        print "Result, found %d elements" % len(search)
        search = self.helper.search_livestate(ls, "downtime:true")
        print "Result, found %d elements" % len(search)
        search = self.helper.search_livestate(ls, "downtime:1")
        print "Result, found %d elements" % len(search)
        search = self.helper.search_livestate(ls, "downtime:false")
        print "Result, found %d elements" % len(search)
        search = self.helper.search_livestate(ls, "downtime:no")
        print "Result, found %d elements" % len(search)
        search = self.helper.search_livestate(ls, "downtime:0")
        print "Result, found %d elements" % len(search)
        assert len(search) > 0
        search = self.helper.search_livestate(ls, "isnot:downtime")
        print "Result, found %d elements" % len(search)
        assert len(search) > 0
        search = self.helper.search_livestate(ls, "is:0")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_livestate(ls, "is:1")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_livestate(ls, "is:2")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_livestate(ls, "is:3")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_livestate(ls, "is:up")
        print "Result, found %d elements" % len(search)
        search = self.helper.search_livestate(ls, "up")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_livestate(ls, "is:down")
        print "Result, found %d elements" % len(search)
        search = self.helper.search_livestate(ls, "down")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_livestate(ls, "is:unreachable")
        print "Result, found %d elements" % len(search)
        search = self.helper.search_livestate(ls, "unreachable")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_livestate(ls, "is:ok")
        print "Result, found %d elements" % len(search)
        search = self.helper.search_livestate(ls, "OK")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_livestate(ls, "is:warning")
        print "Result, found %d elements" % len(search)
        search = self.helper.search_livestate(ls, "WARNING")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_livestate(ls, "is:critical")
        print "Result, found %d elements" % len(search)
        search = self.helper.search_livestate(ls, "CRITICAL")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_livestate(ls, "is:unknown")
        print "Result, found %d elements" % len(search)
        search = self.helper.search_livestate(ls, "UNKNOWN")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_livestate(ls, "is:pending")
        print "Result, found %d elements" % len(search)
        search = self.helper.search_livestate(ls, "PENDING")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_livestate(ls, "isnot:up")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_livestate(ls, "isnot:down")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_livestate(ls, "isnot:unreachable")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_livestate(ls, "isnot:ok")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_livestate(ls, "isnot:warning")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_livestate(ls, "isnot:critical")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_livestate(ls, "isnot:unknown")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_livestate(ls, "isnot:pending")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0

        # Backend disconnection
        frontend.disconnect()

    def test_10_livesynthesis(self):
        print "---"

        # Initialize backend communication ...
        frontend.configure(alignak_webui.app.config.get('ui.backend', 'http://localhost:5000'))
        print "Frontend: %s", frontend.url_endpoint_root

        # Configure users' management backend
        User.set_backend(frontend)

        # Force authentication ...
        connection = frontend.login('admin', 'admin', force=True)
        assert_true(frontend.authenticated)
        assert_true(frontend.token)

        connection = frontend.connect(username='admin')
        assert_true(frontend.authenticated)
        assert_true(frontend.connected)

        print "Get live synthesis ..."
        synthesis = self.helper.get_livesynthesis()
        print "Result:", synthesis
        assert_true('hosts_synthesis' in synthesis)
        assert_true('nb_elts' in synthesis['hosts_synthesis'])
        assert_true('services_synthesis' in synthesis)
        assert_true('nb_elts' in synthesis['services_synthesis'])

        print "Get HTML live synthesis ..."
        synthesis = self.helper.get_html_livesynthesis()
        print "Result:", synthesis
        assert 'hosts_states_popover' in synthesis
        assert 'host state is UP' in synthesis['hosts_states_popover']
        assert 'host state is DOWN' in synthesis['hosts_states_popover']
        assert 'host state is UNREACHABLE' in synthesis['hosts_states_popover']
        assert 'hosts_state' in synthesis
        # assert False

        assert 'services_states_popover' in synthesis
        assert 'service state is OK' in synthesis['services_states_popover']
        assert 'service state is WARNING' in synthesis['services_states_popover']
        assert 'service state is CRITICAL' in synthesis['services_states_popover']
        assert 'services_state' in synthesis

        # Backend disconnection
        frontend.disconnect()

    def test_11_livestate(self):
        print "---"

        # Initialize backend communication ...
        frontend.configure(alignak_webui.app.config.get('ui.backend', 'http://localhost:5000'))
        print "Frontend: %s", frontend.url_endpoint_root

        # Configure users' management backend
        User.set_backend(frontend)

        # Force authentication ...
        connection = frontend.login('admin', 'admin', force=True)
        assert_true(frontend.authenticated)
        assert_true(frontend.token)

        connection = frontend.connect(username='admin')
        assert_true(frontend.authenticated)
        assert_true(frontend.connected)

        print "Get live state ..."
        print "Livestate_age: ", self.helper.livestate_age
        ls = self.helper.get_livestate()
        print "Livestate_age: ", self.helper.livestate_age
        print "Livestate: ", self.helper.livestate
        assert self.helper.livestate_age
        for item in ls:
            print "Item:", item
            assert_true('type' in item)
            assert_true('id' in item)
            assert_true('bi' in item)
            assert_true('name' in item)
            assert_true('friendly_name' in item)
        for item in self.helper.livestate:
            print "Item:", item
            assert_true('type' in item)
            assert_true('id' in item)
            assert_true('bi' in item)
            assert_true('name' in item)
            assert_true('friendly_name' in item)
        assert len(ls) == len(self.helper.livestate)

        print "Get HTML live state ..."
        print "Current user: ", current_user
        html = self.helper.get_html_livestate()
        assert 'bi' in html
        assert 'rows' in html
        assert 'panel_bi' in html
        print "Items:", len(html['rows'])

        for bi in [0,1,2,3,4,5]:
            print "Get HTML live state (BI = %d) ..." % bi
            html = self.helper.get_html_livestate(bi=bi)
            assert 'bi' in html
            assert 'rows' in html
            assert 'panel_bi' in html
            print "Items:", len(html['rows']) / 2
            # for row in html['rows']:
                # print "Item:", row

        print "Get HTML live state ... filter"
        html = self.helper.get_html_livestate(search_filter="type:host")
        assert 'bi' in html
        assert 'rows' in html
        assert 'panel_bi' in html
        print "Items:", len(html['rows'])

        for bi in [0,1,2,3,4,5]:
            print "Get HTML live state (BI = %d) ...and filter" % bi
            html = self.helper.get_html_livestate(bi=bi, search_filter="type:host")
            assert 'bi' in html
            assert 'rows' in html
            assert 'panel_bi' in html
            print "Items:", len(html['rows'])

        # Backend disconnection
        frontend.disconnect()

