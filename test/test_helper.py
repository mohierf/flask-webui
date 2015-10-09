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


    def test_1_print_date(self):
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

    def test_2_print_duration(self):
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

    def test_3_get_business_impact_text(self):
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

    def test_4_get_state_text(self):
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

    def test_5_get_host_state_text(self):
        print "---"

        # Host, icon only (default) ...
        s = self.helper.get_html_state('host', 'UP')
        print "Result:", s
        self.assert_(s == '<span class="font-UP"><span class="fa-stack" title="host state is UP"><i class="fa fa-circle fa-stack-2x font-up"></i><i class="fa fa-server fa-stack-1x fa-inverse"></i></span><span></span></span>')
        s = self.helper.get_html_state('host', 'DOWN')
        print "Result:", s
        self.assert_(s == '<span class="font-DOWN"><span class="fa-stack" title="host state is DOWN"><i class="fa fa-circle fa-stack-2x font-down"></i><i class="fa fa-server fa-stack-1x fa-inverse"></i></span><span></span></span>')
        s = self.helper.get_html_state('host', 'UNREACHABLE')
        print "Result:", s
        self.assert_(s == '<span class="font-UNREACHABLE"><span class="fa-stack" title="host state is UNREACHABLE"><i class="fa fa-circle fa-stack-2x font-unreachable"></i><i class="fa fa-server fa-stack-1x fa-inverse"></i></span><span></span></span>')
        s = self.helper.get_html_state('host', 'UNKNOWN')
        print "Result:", s
        self.assert_(s == '<span class="font-UNKNOWN"><span class="fa-stack" title="host state is UNKNOWN"><i class="fa fa-circle fa-stack-2x font-unknown"></i><i class="fa fa-question fa-stack-1x fa-inverse"></i></span><span></span></span>')
        s = self.helper.get_html_state('host', 'PENDING')
        print "Result:", s
        self.assert_(s == '<span class="font-PENDING"><span class="fa-stack" title="host state is PENDING"><i class="fa fa-circle fa-stack-2x font-pending"></i><i class="fa fa-server fa-stack-1x fa-inverse"></i></span><span></span></span>')
        s = self.helper.get_html_state('host', 'UP', extra='FLAPPING')
        print "Result:", s
        self.assert_(s == '<span class="font-UP"><span class="fa-stack" title="host state is UP and flapping"><i class="fa fa-circle fa-stack-2x font-up"></i><i class="fa fa-server fa-stack-1x font-up"></i></span><span></span></span>')
        s = self.helper.get_html_state('host', 'DOWN', extra='FLAPPING')
        print "Result:", s
        self.assert_(s == '<span class="font-DOWN"><span class="fa-stack" title="host state is DOWN and flapping"><i class="fa fa-circle fa-stack-2x font-down"></i><i class="fa fa-server fa-stack-1x font-down"></i></span><span></span></span>')
        s = self.helper.get_html_state('host', 'DOWN', extra='ACK')
        print "Result:", s
        self.assert_(s == '<span class="font-DOWN"><span class="fa-stack" style="opacity: 0.5" title="host state is DOWN and acknowledged"><i class="fa fa-circle fa-stack-2x font-down"></i><i class="fa fa-server fa-stack-1x fa-inverse"></i></span><span></span></span>')
        s = self.helper.get_html_state('host', 'DOWN', extra='DOWNTIME')
        print "Result:", s
        self.assert_(s == '<span class="font-DOWN"><span class="fa-stack" style="opacity: 0.5" title="host state is DOWN and in scheduled downtime"><i class="fa fa-circle fa-stack-2x font-down"></i><i class="fa fa-server fa-stack-1x fa-inverse"></i></span><span></span></span>')

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
        s = self.helper.get_html_state('host', 'UNKNOWN', text=True, icon=False)
        print "Result:", s
        self.assert_(s == 'host state is UNKNOWN')
        s = self.helper.get_html_state('host', 'PENDING', text=True, icon=False)
        print "Result:", s
        self.assert_(s == 'host state is PENDING')
        s = self.helper.get_html_state('host', 'UP', extra='FLAPPING', text=True, icon=False)
        print "Result:", s
        self.assert_(s == 'host state is UP and flapping')
        s = self.helper.get_html_state('host', 'DOWN', extra='FLAPPING', text=True, icon=False)
        print "Result:", s
        self.assert_(s == 'host state is DOWN and flapping')
        s = self.helper.get_html_state('host', 'DOWN', extra='ACK', text=True, icon=False)
        print "Result:", s
        self.assert_(s == 'host state is DOWN and acknowledged')
        s = self.helper.get_html_state('host', 'DOWN', extra='DOWNTIME', text=True, icon=False)
        print "Result:", s
        self.assert_(s == 'host state is DOWN and in scheduled downtime')

        # Host, icon and text ...
        s = self.helper.get_html_state('host', 'UP', text=True, icon=True)
        print "Result:", s
        self.assert_(s == '<span class="font-UP"><span class="fa-stack" title="host state is UP"><i class="fa fa-circle fa-stack-2x font-up"></i><i class="fa fa-server fa-stack-1x fa-inverse"></i></span><span>host state is UP</span></span>')
        s = self.helper.get_html_state('host', 'DOWN', text=True, icon=True)
        print "Result:", s
        self.assert_(s == '<span class="font-DOWN"><span class="fa-stack" title="host state is DOWN"><i class="fa fa-circle fa-stack-2x font-down"></i><i class="fa fa-server fa-stack-1x fa-inverse"></i></span><span>host state is DOWN</span></span>')
        s = self.helper.get_html_state('host', 'UNREACHABLE', text=True, icon=True)
        print "Result:", s
        self.assert_(s == '<span class="font-UNREACHABLE"><span class="fa-stack" title="host state is UNREACHABLE"><i class="fa fa-circle fa-stack-2x font-unreachable"></i><i class="fa fa-server fa-stack-1x fa-inverse"></i></span><span>host state is UNREACHABLE</span></span>')
        s = self.helper.get_html_state('host', 'UNKNOWN', text=True, icon=True)
        print "Result:", s
        self.assert_(s == '<span class="font-UNKNOWN"><span class="fa-stack" title="host state is UNKNOWN"><i class="fa fa-circle fa-stack-2x font-unknown"></i><i class="fa fa-question fa-stack-1x fa-inverse"></i></span><span>host state is UNKNOWN</span></span>')
        s = self.helper.get_html_state('host', 'PENDING', text=True, icon=True)
        print "Result:", s
        self.assert_(s == '<span class="font-PENDING"><span class="fa-stack" title="host state is PENDING"><i class="fa fa-circle fa-stack-2x font-pending"></i><i class="fa fa-server fa-stack-1x fa-inverse"></i></span><span>host state is PENDING</span></span>')
        s = self.helper.get_html_state('host', 'UP', extra='FLAPPING', text=True, icon=True)
        print "Result:", s
        self.assert_(s == '<span class="font-UP"><span class="fa-stack" title="host state is UP and flapping"><i class="fa fa-circle fa-stack-2x font-up"></i><i class="fa fa-server fa-stack-1x font-up"></i></span><span>host state is UP and flapping</span></span>')
        s = self.helper.get_html_state('host', 'DOWN', extra='FLAPPING', text=True, icon=True)
        print "Result:", s
        self.assert_(s == '<span class="font-DOWN"><span class="fa-stack" title="host state is DOWN and flapping"><i class="fa fa-circle fa-stack-2x font-down"></i><i class="fa fa-server fa-stack-1x font-down"></i></span><span>host state is DOWN and flapping</span></span>')
        s = self.helper.get_html_state('host', 'DOWN', extra='ACK', text=True, icon=True)
        print "Result:", s
        self.assert_(s == '<span class="font-DOWN"><span class="fa-stack" style="opacity: 0.5" title="host state is DOWN and acknowledged"><i class="fa fa-circle fa-stack-2x font-down"></i><i class="fa fa-server fa-stack-1x fa-inverse"></i></span><span>host state is DOWN and acknowledged</span></span>')
        s = self.helper.get_html_state('host', 'DOWN', extra='DOWNTIME', text=True, icon=True)
        print "Result:", s
        self.assert_(s == '<span class="font-DOWN"><span class="fa-stack" style="opacity: 0.5" title="host state is DOWN and in scheduled downtime"><i class="fa fa-circle fa-stack-2x font-down"></i><i class="fa fa-server fa-stack-1x fa-inverse"></i></span><span>host state is DOWN and in scheduled downtime</span></span>')

    def test_6_get_service_state_text(self):
        print "---"

        # service, icon only (default) ...
        s = self.helper.get_html_state('service', 'OK')
        print "Result:", s
        self.assert_(s == '<span class="font-OK"><span class="fa-stack" title="service state is OK"><i class="fa fa-circle fa-stack-2x font-ok"></i><i class="fa fa-arrow-up fa-stack-1x fa-inverse"></i></span><span></span></span>')
        s = self.helper.get_html_state('service', 'CRITICAL')
        print "Result:", s
        self.assert_(s == '<span class="font-CRITICAL"><span class="fa-stack" title="service state is CRITICAL"><i class="fa fa-circle fa-stack-2x font-critical"></i><i class="fa fa-arrow-down fa-stack-1x fa-inverse"></i></span><span></span></span>')
        s = self.helper.get_html_state('service', 'WARNING')
        print "Result:", s
        self.assert_(s == '<span class="font-WARNING"><span class="fa-stack" title="service state is WARNING"><i class="fa fa-circle fa-stack-2x font-warning"></i><i class="fa fa-exclamation fa-stack-1x fa-inverse"></i></span><span></span></span>')
        s = self.helper.get_html_state('service', 'UNKNOWN')
        print "Result:", s
        self.assert_(s == '<span class="font-UNKNOWN"><span class="fa-stack" title="service state is UNKNOWN"><i class="fa fa-circle fa-stack-2x font-unknown"></i><i class="fa fa-question fa-stack-1x fa-inverse"></i></span><span></span></span>')
        s = self.helper.get_html_state('service', 'PENDING')
        print "Result:", s
        self.assert_(s == '<span class="font-PENDING"><span class="fa-stack" title="service state is PENDING"><i class="fa fa-circle fa-stack-2x font-pending"></i><i class="fa fa-spinner fa-circle-o-notch fa-stack-1x fa-inverse"></i></span><span></span></span>')
        s = self.helper.get_html_state('service', 'OK', extra='FLAPPING')
        print "Result:", s
        self.assert_(s == '<span class="font-OK"><span class="fa-stack" title="service state is OK and flapping"><i class="fa fa-circle fa-stack-2x font-ok"></i><i class="fa fa-arrow-up fa-stack-1x font-ok"></i></span><span></span></span>')
        s = self.helper.get_html_state('service', 'CRITICAL', extra='FLAPPING')
        print "Result:", s
        self.assert_(s == '<span class="font-CRITICAL"><span class="fa-stack" title="service state is CRITICAL and flapping"><i class="fa fa-circle fa-stack-2x font-critical"></i><i class="fa fa-arrow-down fa-stack-1x font-critical"></i></span><span></span></span>')
        s = self.helper.get_html_state('service', 'CRITICAL', extra='ACK')
        print "Result:", s
        self.assert_(s == '<span class="font-CRITICAL"><span class="fa-stack" style="opacity: 0.5" title="service state is CRITICAL and acknowledged"><i class="fa fa-circle fa-stack-2x font-critical"></i><i class="fa fa-arrow-down fa-stack-1x fa-inverse"></i></span><span></span></span>')
        s = self.helper.get_html_state('service', 'CRITICAL', extra='DOWNTIME')
        print "Result:", s
        self.assert_(s == '<span class="font-CRITICAL"><span class="fa-stack" style="opacity: 0.5" title="service state is CRITICAL and in scheduled downtime"><i class="fa fa-circle fa-stack-2x font-critical"></i><i class="fa fa-arrow-down fa-stack-1x fa-inverse"></i></span><span></span></span>')

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
        s = self.helper.get_html_state('service', 'PENDING', text=True, icon=False)
        print "Result:", s
        self.assert_(s == 'service state is PENDING')
        s = self.helper.get_html_state('service', 'OK', extra='FLAPPING', text=True, icon=False)
        print "Result:", s
        self.assert_(s == 'service state is OK and flapping')
        s = self.helper.get_html_state('service', 'CRITICAL', extra='FLAPPING', text=True, icon=False)
        print "Result:", s
        self.assert_(s == 'service state is CRITICAL and flapping')
        s = self.helper.get_html_state('service', 'CRITICAL', extra='ACK', text=True, icon=False)
        print "Result:", s
        self.assert_(s == 'service state is CRITICAL and acknowledged')
        s = self.helper.get_html_state('service', 'CRITICAL', extra='DOWNTIME', text=True, icon=False)
        print "Result:", s
        self.assert_(s == 'service state is CRITICAL and in scheduled downtime')

        # service, icon and text ...
        s = self.helper.get_html_state('service', 'OK', text=True, icon=True)
        print "Result:", s
        self.assert_(s == '<span class="font-OK"><span class="fa-stack" title="service state is OK"><i class="fa fa-circle fa-stack-2x font-ok"></i><i class="fa fa-arrow-up fa-stack-1x fa-inverse"></i></span><span>service state is OK</span></span>')
        s = self.helper.get_html_state('service', 'CRITICAL', text=True, icon=True)
        print "Result:", s
        self.assert_(s == '<span class="font-CRITICAL"><span class="fa-stack" title="service state is CRITICAL"><i class="fa fa-circle fa-stack-2x font-critical"></i><i class="fa fa-arrow-down fa-stack-1x fa-inverse"></i></span><span>service state is CRITICAL</span></span>')
        s = self.helper.get_html_state('service', 'WARNING', text=True, icon=True)
        print "Result:", s
        self.assert_(s == '<span class="font-WARNING"><span class="fa-stack" title="service state is WARNING"><i class="fa fa-circle fa-stack-2x font-warning"></i><i class="fa fa-exclamation fa-stack-1x fa-inverse"></i></span><span>service state is WARNING</span></span>')
        s = self.helper.get_html_state('service', 'UNKNOWN', text=True, icon=True)
        print "Result:", s
        self.assert_(s == '<span class="font-UNKNOWN"><span class="fa-stack" title="service state is UNKNOWN"><i class="fa fa-circle fa-stack-2x font-unknown"></i><i class="fa fa-question fa-stack-1x fa-inverse"></i></span><span>service state is UNKNOWN</span></span>')
        s = self.helper.get_html_state('service', 'PENDING', text=True, icon=True)
        print "Result:", s
        self.assert_(s == '<span class="font-PENDING"><span class="fa-stack" title="service state is PENDING"><i class="fa fa-circle fa-stack-2x font-pending"></i><i class="fa fa-spinner fa-circle-o-notch fa-stack-1x fa-inverse"></i></span><span>service state is PENDING</span></span>')
        s = self.helper.get_html_state('service', 'OK', extra='FLAPPING', text=True, icon=True)
        print "Result:", s
        self.assert_(s == '<span class="font-OK"><span class="fa-stack" title="service state is OK and flapping"><i class="fa fa-circle fa-stack-2x font-ok"></i><i class="fa fa-arrow-up fa-stack-1x font-ok"></i></span><span>service state is OK and flapping</span></span>')
        s = self.helper.get_html_state('service', 'CRITICAL', extra='FLAPPING', text=True, icon=True)
        print "Result:", s
        self.assert_(s == '<span class="font-CRITICAL"><span class="fa-stack" title="service state is CRITICAL and flapping"><i class="fa fa-circle fa-stack-2x font-critical"></i><i class="fa fa-arrow-down fa-stack-1x font-critical"></i></span><span>service state is CRITICAL and flapping</span></span>')
        s = self.helper.get_html_state('service', 'CRITICAL', extra='ACK', text=True, icon=True)
        print "Result:", s
        self.assert_(s == '<span class="font-CRITICAL"><span class="fa-stack" style="opacity: 0.5" title="service state is CRITICAL and acknowledged"><i class="fa fa-circle fa-stack-2x font-critical"></i><i class="fa fa-arrow-down fa-stack-1x fa-inverse"></i></span><span>service state is CRITICAL and acknowledged</span></span>')
        s = self.helper.get_html_state('service', 'CRITICAL', extra='DOWNTIME', text=True, icon=True)
        print "Result:", s
        self.assert_(s == '<span class="font-CRITICAL"><span class="fa-stack" style="opacity: 0.5" title="service state is CRITICAL and in scheduled downtime"><i class="fa fa-circle fa-stack-2x font-critical"></i><i class="fa fa-arrow-down fa-stack-1x fa-inverse"></i></span><span>service state is CRITICAL and in scheduled downtime</span></span>')

        # Use label instead of built text ...
        s = self.helper.get_html_state('service', 'OK', text=True, icon=True, label='My own label')
        print "Result:", s
        self.assert_(s == '<span class="font-OK"><span class="fa-stack" title="service state is OK"><i class="fa fa-circle fa-stack-2x font-ok"></i><i class="fa fa-arrow-up fa-stack-1x fa-inverse"></i></span><span>My own label</span></span>')

        # Specify disabled state ...
        s = self.helper.get_html_state('service', 'OK', text=True, icon=True, label='My own label', disabled=True)
        print "Result:", s
        self.assert_(s == '<span class="font-OK"><span class="fa-stack" title="service state is OK"><i class="fa fa-circle fa-stack-2x font-greyed"></i><i class="fa fa-arrow-up fa-stack-1x fa-inverse"></i></span><span>My own label</span></span>')

    def test_7_get_url(self):
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

    def test_8_livestate(self):
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
        assert 'hosts_states' in synthesis
        assert 'host state is UP' in synthesis['hosts_states']
        assert 'host state is DOWN' in synthesis['hosts_states']
        assert 'host state is UNREACHABLE' in synthesis['hosts_states']
        assert 'services_states' in synthesis
        assert 'service state is OK' in synthesis['services_states']
        assert 'service state is WARNING' in synthesis['services_states']
        assert 'service state is CRITICAL' in synthesis['services_states']

        print "Get live state ..."
        s = self.helper.get_livestate()
        print "Result:", s

        # Backend disconnection
        frontend.disconnect()

    def test_9_search(self):
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

        print "Search on element type ..."
        search = self.helper.search_hosts_and_services("type:all")
        print "Result, found %d elements" % len(search)
        search = self.helper.search_hosts_and_services("type:host")
        print "Result, found %d elements" % len(search)
        search = self.helper.search_hosts_and_services("type:service")
        print "Result, found %d elements" % len(search)
        search = self.helper.search_hosts_and_services("host")
        print "Result, found %d elements" % len(search)
        search = self.helper.search_hosts_and_services("service")
        print "Result, found %d elements" % len(search)
        search = self.helper.search_hosts_and_services("type:unknown")
        print "Result, found %d elements" % len(search)

        print "---"
        print "Search on element name and content ... "
        print "found in name ..."
        search = self.helper.search_hosts_and_services("charnay")
        print "Result, found %d elements" % len(search)
        assert len(search) > 0
        print "found in output ..."
        search = self.helper.search_hosts_and_services("time")
        print "Result, found %d elements" % len(search)
        assert len(search) > 0
        print "not found ..."
        search = self.helper.search_hosts_and_services("test")
        print "Result, found %d elements" % len(search)

        print "---"
        print "Search on element business impact ... "
        search = self.helper.search_hosts_and_services("bi:0")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_hosts_and_services("bi:=0")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_hosts_and_services("bi:>0")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_hosts_and_services("bi:>=0")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_hosts_and_services("bi:<5")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_hosts_and_services("bi:<=5")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_hosts_and_services("bi:>3")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0

        print "---"
        print "Search on element state ... "
        search = self.helper.search_hosts_and_services("is:ack")
        print "Result, found %d elements" % len(search)
        search = self.helper.search_hosts_and_services("ack:true")
        print "Result, found %d elements" % len(search)
        search = self.helper.search_hosts_and_services("ack:yes")
        print "Result, found %d elements" % len(search)
        search = self.helper.search_hosts_and_services("ack:1")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_hosts_and_services("isnot:ack")
        print "Result, found %d elements" % len(search)
        search = self.helper.search_hosts_and_services("ack:false")
        print "Result, found %d elements" % len(search)
        search = self.helper.search_hosts_and_services("ack:no")
        print "Result, found %d elements" % len(search)
        search = self.helper.search_hosts_and_services("ack:0")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        # search = self.helper.search_hosts_and_services("is:downtime")
        # print "Result, found %d elements" % len(search)
        # search = self.helper.search_hosts_and_services("downtime:yes")
        # print "Result, found %d elements" % len(search)
        # search = self.helper.search_hosts_and_services("downtime:true")
        # print "Result, found %d elements" % len(search)
        # search = self.helper.search_hosts_and_services("downtime:1")
        # print "Result, found %d elements" % len(search)
        # search = self.helper.search_hosts_and_services("downtime:false")
        # print "Result, found %d elements" % len(search)
        # search = self.helper.search_hosts_and_services("downtime:no")
        # print "Result, found %d elements" % len(search)
        # search = self.helper.search_hosts_and_services("downtime:0")
        # print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        # search = self.helper.search_hosts_and_services("isnot:downtime")
        # print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        # search = self.helper.search_hosts_and_services("is:impact")
        # print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        # search = self.helper.search_hosts_and_services("isnot:impact")
        # print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_hosts_and_services("is:0")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_hosts_and_services("is:1")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_hosts_and_services("is:2")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_hosts_and_services("is:3")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_hosts_and_services("is:up")
        print "Result, found %d elements" % len(search)
        search = self.helper.search_hosts_and_services("up")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_hosts_and_services("is:down")
        print "Result, found %d elements" % len(search)
        search = self.helper.search_hosts_and_services("down")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_hosts_and_services("is:unreachable")
        print "Result, found %d elements" % len(search)
        search = self.helper.search_hosts_and_services("unreachable")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_hosts_and_services("is:ok")
        print "Result, found %d elements" % len(search)
        search = self.helper.search_hosts_and_services("OK")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_hosts_and_services("is:warning")
        print "Result, found %d elements" % len(search)
        search = self.helper.search_hosts_and_services("WARNING")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_hosts_and_services("is:critical")
        print "Result, found %d elements" % len(search)
        search = self.helper.search_hosts_and_services("CRITICAL")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_hosts_and_services("is:unknown")
        print "Result, found %d elements" % len(search)
        search = self.helper.search_hosts_and_services("UNKNOWN")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_hosts_and_services("is:pending")
        print "Result, found %d elements" % len(search)
        search = self.helper.search_hosts_and_services("PENDING")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_hosts_and_services("isnot:up")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_hosts_and_services("isnot:down")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_hosts_and_services("isnot:unreachable")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_hosts_and_services("isnot:ok")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_hosts_and_services("isnot:warning")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_hosts_and_services("isnot:critical")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_hosts_and_services("isnot:unknown")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0
        search = self.helper.search_hosts_and_services("isnot:pending")
        print "Result, found %d elements" % len(search)
        # assert len(search) > 0

        # Backend disconnection
        frontend.disconnect()

    def test_10_get_id(self):
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
