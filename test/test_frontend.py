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

from nose import with_setup # optional
from nose.tools import *

def setup_module(module):
    print ("") # this is to get a newline after the dots
    print ("setup_module before anything in this file")

def teardown_module(module):
    print ("") # this is to get a newline after the dots
    print ("teardown_module after everything in this file")



import alignak_webui
from alignak_webui.backend import FrontEnd, BackendException
from alignak_webui import app, frontend, manifest, settings
from alignak_webui.user import User
from alignak_webui.utils.settings import Settings
from alignak_webui.utils.helper import Helper


# extend the class unittest.TestCase
class test_frontend(unittest.TestCase):

    appli = None

    def setUp(self):
        print ""
        print "setting up ..."

        alignak_webui.app.config['HOST'] = '127.0.0.1'
        alignak_webui.app.config['PORT'] = 80
        alignak_webui.app.config['DEBUG'] = False

        alignak_webui.app.config['TESTING'] = True

        sett = Settings(alignak_webui.app)
        found_cfg_files = sett.read("settings.cfg", {})

        self.helper = Helper(alignak_webui.app)

        # Initialize backend communication ...
        self.frontend = FrontEnd(settings.get('ui.backend', 'http://localhost:5000'))
        print "Frontend: %s", self.frontend.url_endpoint_root

        # Configure users' management backend
        User.set_backend(self.frontend)

    def tearDown(self):
        print ""
        print "tearing down ..."


    def test_0_config(self):
        print ''
        print 'test config'

        print "Frontend: %s", self.frontend.url_endpoint_root
        print 'object:', self.frontend
        print 'connected:', self.frontend.connected
        print 'initialized:', self.frontend.initialized
        print 'authenticated:', self.frontend.authenticated
        assert_false(self.frontend.connected)

    def test_1_not_available(self):
        print ''
        print 'test not available'

        print 'object:', self.frontend
        print 'connected:', self.frontend.connected
        print 'initialized:', self.frontend.initialized
        print 'authenticated:', self.frontend.authenticated
        # Must be False, not yet connected ...
        assert_false(self.frontend.connected)
        assert_false(self.frontend.authenticated)

    def test_2_refused_connection_username(self):
        print ''
        print 'test refused connection with username/password'

        connection = self.frontend.login('admin', 'bad_password')
        assert_false(self.frontend.authenticated)

        connection = self.frontend.connect('admin', 'bad_password')
        assert_false(self.frontend.connected)
        assert_false(self.frontend.authenticated)

    def test_3_refused_connection_token(self):
        print ''
        print 'test refused connection with token'

        with assert_raises(BackendException) as cm:
            print 'authenticated:', self.frontend.authenticated
            connection = self.frontend.connect(token='anything')
            print 'authenticated:', self.frontend.authenticated
        ex = cm.exception # raised exception is available through exception property of context
        print 'exception:', str(ex.code)
        assert_true(ex.code == 1001, str(ex))
        assert_false(self.frontend.connected)
        assert_false(self.frontend.authenticated)

    def test_4_connection_username(self):
        print ''
        print 'test connection with username/password'

        connection = self.frontend.login('admin', 'admin')
        assert_true(self.frontend.authenticated)
        assert_false(self.frontend.connected)
        assert_true(self.frontend.token)

        connection = self.frontend.logout()
        assert_false(self.frontend.authenticated)
        assert_false(self.frontend.connected)
        assert_false(self.frontend.token)

        print 'authenticated:', self.frontend.authenticated
        connection = self.frontend.connect('admin', 'admin')
        print 'authenticated:', self.frontend.authenticated
        assert_true(self.frontend.connected)
        assert_true(self.frontend.authenticated)
        assert_true(self.frontend.token)

        connection = self.frontend.disconnect()
        assert_false(self.frontend.authenticated)
        assert_false(self.frontend.connected)
        assert_false(self.frontend.token)

    def test_5_connection_token(self):
        print ''
        print 'test connection with token'

        # print 'token only connection refused ...'
        # with assert_raises(BackendException) as cm:
            # print 'authenticated:', self.frontend.authenticated
            # connection = self.frontend.connect(token='anything')
            # print 'authenticated:', self.frontend.authenticated
        # ex = cm.exception # raised exception is available through exception property of context
        # print 'exception:', str(ex.code)
        # assert_true(ex.code == 1001, str(ex))
        # assert_false(self.frontend.connected)
        # assert_false(self.frontend.authenticated)

        print 'username/password authentication ...'
        # assert_false(self.frontend.authenticated)
        connection = self.frontend.connect('admin', 'admin')
        print 'authenticated:', self.frontend.authenticated
        assert_true(self.frontend.authenticated)
        assert_true(connection)

        print 'token only connection refused ... bad token'
        assert_true(self.frontend.authenticated)
        connection = self.frontend.connect(token='1442583814636-bed32565-2ff7-4023-87fb-34a3ac93d34c')
        print 'authenticated:', self.frontend.authenticated
        assert_false(self.frontend.authenticated)
        assert_false(connection)

        print 'username/password authentication ...'
        assert_false(self.frontend.authenticated)
        connection = self.frontend.connect('admin', 'admin')
        print 'authenticated:', self.frontend.authenticated
        assert_true(self.frontend.authenticated)
        assert_true(connection)

        print 'token only connection accepted ...'
        assert_true(self.frontend.authenticated)
        connection = self.frontend.connect(token=self.frontend.token)
        print 'authenticated:', self.frontend.authenticated
        assert_true(self.frontend.authenticated)
        assert_true(connection)

    def test_6_all_domains(self):
        print ''
        print 'get all domains'

        # Backend connection
        connection = self.frontend.connect('admin', 'admin')
        assert_true(connection)

        # Get all pages
        print 'get all elements at once'
        # Filter the templates ...
        for object_type in self.frontend.backend_available_objets:
            items = self.frontend.get_objects(object_type["title"], parameters=None, all_elements=False)
            print "Got %d %ss:" % (len(items), object_type)

            items = self.frontend.get_ui_data_model(object_type["title"])
            print "Got %d %ss:" % (len(items), object_type)
            # assert_true('_items' not in items)

        # Backend connection
        self.frontend.disconnect()

    def test_6_all_pages(self):
        print ''
        print 'get all elements on an endpoint'

        # Backend connection
        connection = self.frontend.connect('admin', 'admin')
        print connection
        assert_true(connection)

        # Get all pages
        print 'get all elements at once'
        # Filter the templates ...
        parameters = { 'where': '{"register":true}' }
        items = self.frontend.get_objects('host', parameters=parameters, all_elements=True)
        print "Got %s elements:" % len(items)
        assert_true('_items' not in items)
        # assert_true(len(items) > 0)
        for item in items:
            assert_true('host_name' in item)
            print "Host: ", item['host_name']

        # Get all pages
        print 'get all elements at once'
        # Filter the templates ...
        parameters = { 'where': '{"register":true}' }
        items = self.frontend.get_objects('service', parameters=parameters, all_elements=True)
        print "Got %s elements:" % len(items)
        assert_true('_items' not in items)
        # assert_true(len(items) > 0)
        for item in items:
            assert_true('host_name' in item)
            assert_true('service_description' in item)
            print "Service: %s/%s" % (item['host_name'], item['service_description'])

    def test_6_page_after_page(self):
        print ''
        print 'backend connection with username/password'

        # Backend connection
        connection = self.frontend.connect('admin', 'admin')
        assert_true(connection)

        # Start with first page ...
        last_page = False
        parameters = { 'where': '{"register":false}', 'max_results': 10, 'page': 1 }
        items = []
        while not last_page:
            resp = self.frontend.get_objects('host', parameters=parameters, all_elements=False)
            assert_true('_items' in resp)
            assert_true('_links' in resp)
            assert_true('_meta' in resp)
            print resp['_meta']
            page_number = int(resp['_meta']['page'])
            total = int(resp['_meta']['total'])
            max_results = int(resp['_meta']['max_results'])
            print "Got %d elements out of %d (page %d):" % (max_results, total, page_number)
            for item in resp['_items']:
                assert_true('host_name' in item)
                print "Host: ", item['host_name']

            if 'next' in resp['_links']:
                # It has pagination, so get items of all pages
                parameters['page'] = page_number + 1
                parameters['max_results'] = max_results
            else:
                last_page = True
            items.extend(resp['_items'])

        print "----------"
        print "Got %s elements:" % len(items)
        assert_true('_items' not in items)
        # assert_true(len(items) > 0)
        for item in items:
            assert_true('host_name' in item)
            print "Host: ", item['host_name']

        # Start with first page ...
        last_page = False
        parameters = { 'where': '{"register":true}', 'max_results': 10, 'page': 1 }
        items = []
        while not last_page:
            resp = self.frontend.get_objects('service', parameters=parameters, all_elements=False)
            assert_true('_items' in resp)
            assert_true('_links' in resp)
            assert_true('_meta' in resp)
            print resp['_meta']
            page_number = int(resp['_meta']['page'])
            total = int(resp['_meta']['total'])
            max_results = int(resp['_meta']['max_results'])
            print "Got %d elements out of %d (page %d):" % (max_results, total, page_number)
            for item in resp['_items']:
                assert_true('host_name' in item)
                assert_true('service_description' in item)
                print "Service: %s/%s" % (item['host_name'], item['service_description'])

            if 'next' in resp['_links']:
                # It has pagination, so get items of all pages
                parameters['page'] = page_number + 1
                parameters['max_results'] = max_results
            else:
                last_page = True
            items.extend(resp['_items'])

        print "----------"
        print "Got %s elements:" % len(items)
        assert_true('_items' not in items)
        # assert_true(len(items) > 0)
        for item in items:
            assert_true('host_name' in item)
            assert_true('service_description' in item)
            print "Service: %s/%s" % (item['host_name'], item['service_description'])

    def test_7_user_preferences(self):
        print ''
        print 'test user preferences'

        connection = self.frontend.login('admin', 'admin')
        assert_true(self.frontend.authenticated)
        assert_false(self.frontend.connected)
        assert_true(self.frontend.token)

        parameters = {'a': 1, 'b': '2'}
        response = self.frontend.set_user_preferences('admin', 'test_prefs', parameters)
        # {u'_updated': u'Sun, 04 Oct 2015 08:14:41 GMT', u'_links': {u'self': {u'href': u'uipref/5610dff1f9e3854415d129be', u'title': u'Uipref'}}, u'_created': u'Sun, 04 Oct 2015 08:14:41 GMT', u'_status': u'OK', u'_id': u'5610dff1f9e3854415d129be', u'_etag': u'26569a70b70d9ea2f5df5983a685c41278db23cf'}
        print response
        assert_true('_updated' in response)

        parameters = self.frontend.get_user_preferences('admin', 'test_prefs')
        # u'_updated': u'Sun, 04 Oct 2015 08:19:08 GMT', u'data': {u'a': 1, u'b': u'2'}, u'_links': {u'self': {u'href': u'uipref/5610dff1f9e3854415d129be', u'title': u'Uipref'}}, u'user': u'admin', u'_created': u'Sun, 04 Oct 2015 08:14:41 GMT', u'_id': u'5610dff1f9e3854415d129be', u'type': u'test_prefs', u'_etag': u'8c05b7d8ee64d18e10a98a7885569c48f4a68d13'}
        print parameters
        assert_true('data' in parameters)
        assert_true('a' in parameters['data'])
        assert_true(parameters['data']['a'] == 1)
        assert_true('b' in parameters['data'])
        assert_true(parameters['data']['b'] == '2')

        parameters = {'a': 2, 'b': '3'}
        response = self.frontend.set_user_preferences('admin', 'test_prefs', parameters)
        print response
        assert_true('_updated' in response)

        parameters = self.frontend.get_user_preferences('admin', 'test_prefs')
        # u'_updated': u'Sun, 04 Oct 2015 08:19:08 GMT', u'data': {u'a': 1, u'b': u'2'}, u'_links': {u'self': {u'href': u'uipref/5610dff1f9e3854415d129be', u'title': u'Uipref'}}, u'user': u'admin', u'_created': u'Sun, 04 Oct 2015 08:14:41 GMT', u'_id': u'5610dff1f9e3854415d129be', u'type': u'test_prefs', u'_etag': u'8c05b7d8ee64d18e10a98a7885569c48f4a68d13'}
        print parameters
        assert_true('data' in parameters)
        assert_true('a' in parameters['data'])
        assert_true(parameters['data']['a'] == 2)
        assert_true('b' in parameters['data'])
        assert_true(parameters['data']['b'] == '3')

        connection = self.frontend.logout()
        assert_false(self.frontend.authenticated)
        assert_false(self.frontend.connected)
        assert_false(self.frontend.token)

    def test_8_livestate(self):
        print ''
        print 'get livestate'

        # Backend connection
        connection = self.frontend.connect('admin', 'admin')
        assert_true(connection)

        print 'get livetstate elements'
        items = self.frontend.get_livestate(parameters=None)
        print "Got %d elements" % (len(items))
        print items

        print 'get livetstate hosts'
        items = self.frontend.get_livestate_hosts(parameters=None)
        print "Got %d elements" % (len(items))
        print items[0]

        print 'get livetstate hosts'
        parameters = { 'where': '{"register":true}' }
        items = self.frontend.get_livestate_hosts(parameters=parameters)
        print "Got %d elements" % (len(items))
        print items[0]

        print 'get livetstate services'
        parameters = { 'where': '{"register":true}' }
        items = self.frontend.get_livestate_services(parameters=parameters)
        print "Got %d elements" % (len(items))
        print items[0]

        print 'get livetstate services'
        items = self.frontend.get_livestate_services(parameters=None)
        print "Got %d elements" % (len(items))
        print items[0]

        # Backend connection
        self.frontend.disconnect()

    def test_9_livesynthesis(self):
        print ''
        print 'get live synthesis'

        # Backend connection
        connection = self.frontend.connect('admin', 'admin')
        assert_true(connection)

        print 'get live synthesis'
        synthesis = self.frontend.get_livesynthesis()
        print synthesis
        assert_true('hosts_synthesis' in synthesis)
        assert_true('nb_elts' in synthesis['hosts_synthesis'])
        assert_true('services_synthesis' in synthesis)
        assert_true('nb_elts' in synthesis['services_synthesis'])

        print 'get hosts live synthesis'
        synthesis = self.frontend.get_hosts_synthesis()
        print synthesis
        assert_true('nb_elts' in synthesis)

        print 'get services live synthesis'
        synthesis = self.frontend.get_services_synthesis()
        print synthesis
        assert_true('nb_elts' in synthesis)

        # Backend connection
        self.frontend.disconnect()
