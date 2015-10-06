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
import json
import unittest

from nose import with_setup # optional
from nose.tools import *

def setup_module(module):
    print ("") # this is to get a newline after the dots
    print ("setup_module before anything in this file")

    app.testing = True

    # Load application settings
    sett = Settings(app)
    found_cfg_files = sett.read("settings.cfg", {})

    # Initialize backend communication ...
    frontend.configure(app.config.get('ui.backend', 'http://localhost:5000'))
    print "Frontend: %s", frontend.url_endpoint_root

    # Configure users' management backend
    User.set_backend(frontend)

    # Application current directory, find plugins directory ...
    app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))

    # Load application plugins
    plugins = Plugins(app)
    plugins_dir = os.path.join(
        os.path.join(app_dir, manifest['name'].lower()),
        app.config.get('ui.plugins_dir', 'plugins')
    )
    plugins.load_plugins(plugins_dir)

def teardown_module(module):
    print ("") # this is to get a newline after the dots
    print ("teardown_module after everything in this file")

    connection = frontend.disconnect()
    assert_false(frontend.connected)


import alignak_webui
from alignak_webui import app, frontend, manifest, settings
from alignak_webui.backend import FrontEnd, BackendException
from alignak_webui import views
from alignak_webui.user import User
from alignak_webui.datatable import Datatable
from alignak_webui.utils.settings import Settings
from alignak_webui.utils.helper import Helper
from alignak_webui.utils.plugins import Plugins



class test_datatable(unittest.TestCase):

    object_type = None
    app = None
    table = None

    def setUp(self):
        print ""
        print "setting up ..."

        self.app = app.test_client()

        # Login
        rv = self.app.post('/login', data=dict(
            username='admin', password='admin'
        ), follow_redirects=True)

        self.object_type='host'

    def tearDown(self):
        print 'teardown ...'

        # Logout
        self.app.get('/logout')

    def test_1(self):
        print ''

        print 'Get element fields for UI: %s' % self.object_type
        fields_list = []
        fields=frontend.get_ui_data_model(self.object_type)
        print 'Got ', len(fields), ' items'
        ok_(len(fields))
        for field in fields:
            if 'ui' in field:
                print 'Field ', field

    def test_2(self):
        print ''

        # Get hosts data
        print 'get hosts preferences - bad url'
        resp = self.app.get('/get_prefs/host')
        ok_(resp.status_code == 404)
        ok_('404 NOT FOUND' in resp.status)

        print 'get hosts preferences without parameters'
        expected = {
        }
        rv = self.app.get('/hosts/get_prefs')
        print "Status: %d, '%s'" % (rv.status_code, rv.status)
        ok_(rv.status_code == 200)
        ok_(rv.status == '200 OK')
        # self.assertEqual(json.loads(rv.data), expected)

        print 'get hosts preferences with parameters'
        parameters = {
            'user': 'admin', 'type': 'test'
        }
        expected = {
        }
        rv = self.app.get('/hosts/get_prefs', query_string=parameters)
        print "Status: %d, '%s'" % (rv.status_code, rv.status)
        ok_(rv.status_code == 200)
        ok_(rv.status == '200 OK')
        # ok_(rv.data)
        print "Data: %s" % (rv.data)
        # self.assertEqual(json.loads(rv.data), expected)

        print 'set hosts preferences without parameters'
        resp = self.app.post('/hosts/set_prefs')
        print "Status: %d, '%s'" % (resp.status_code, resp.status)
        ok_(resp.status_code == 400)
        ok_(resp.status == '400 BAD REQUEST')

        print 'set hosts preferences with parameters'
        parameters = {
            'user': 'admin', 'type': 'test',
            'data': json.dumps({'a': 1, 'b': '2'})
        }
        expected = {
            u'_updated': u'Mon, 05 Oct 2015 17:03:51 GMT', u'_links': {u'self': {u'href': u'uipref/5612ad77f9e3854415d129c0', u'title': u'Uipref'}}, u'_created': u'Mon, 05 Oct 2015 17:03:51 GMT', u'_status': u'OK', u'_id': u'5612ad77f9e3854415d129c0', u'_etag': u'8dc871452d0f85509ff67700fc5c1635af3ffc69'
        }
        rv = self.app.post('/hosts/set_prefs', data=parameters)
        print "Status: %d, '%s'" % (rv.status_code, rv.status)
        ok_(rv.status_code == 200)
        ok_(rv.status == '200 OK')
        print "Data: %s" % (rv.data)
        json_data = json.loads(rv.data)
        ok_('_id' in json_data)
        ok_('_status' in json_data)
        ok_(json_data['_status'] == 'OK')

        print 'get hosts preferences'
        parameters = {
            'user': 'admin', 'type': 'test'
        }
        expected = {
        }
        rv = self.app.get('/hosts/get_prefs', query_string=parameters)
        print "Status: %d, '%s'" % (rv.status_code, rv.status)
        ok_(rv.status_code == 200)
        ok_(rv.status == '200 OK')
        ok_(rv.data)
        print "Data: %s" % (rv.data)
        json_data = json.loads(rv.data)
        ok_('a' in json_data)
        ok_(json_data['a'] == 1)
        ok_('b' in json_data)
        ok_(json_data['b'] == '2')


    def test_3(self):
        # Get hosts data
        # Max results
        print 'get hosts table ...'
        rv = self.app.get('/hosts')
        ok_(rv.status_code == 200)
        ok_(rv.status == '200 OK')
        # ok_(rv.data == '')
        print "Data: %s" % (rv.data)
        ok_("$('#tbl_host').DataTable" in rv.data)

        # Get hosts data
        # Max results and projection
        print 'get hosts data, max length is 1, projection to get only name and host_name'
        columns = {
            "columns[0][data]": "host_name",
            "columns[0][name]": "",
            "columns[0][searchable]": "true",
            "columns[0][orderable]": "true",
            "columns[0][search][value]": "",
            "columns[0][search][regexp]": "false",
            "columns[1][data]": "host_name",
            "columns[1][name]": "",
            "columns[1][searchable]": "true",
            "columns[1][orderable]": "true",
            "columns[1][search][value]": "",
            "columns[1][search][regexp]": "false",
        }
        parameters = { 'length': 1 }
        parameters.update(columns)
        print "parameters: ", parameters
        rv = self.app.get('/hosts/data', query_string=parameters)
        print "Status: %d, '%s'" % (rv.status_code, rv.status)
        ok_(rv.status_code == 200)
        ok_(rv.status == '200 OK')
        ok_(rv.data)
        print "Data: %s" % (rv.data)
        json_data = json.loads(rv.data)
        print "JSON Data: %s" % (json_data)
        ok_('recordsTotal' in json_data)
        ok_('recordsFiltered' in json_data)
        ok_('draw' in json_data)
        ok_('data' in json_data)
        i = 0
        for line in json_data['data']:
            print line['host_name']
            i = i + 1
        ok_(i == 1)

        # Get hosts data
        # Max results and projection
        print 'get hosts data, max length is 1, projection to get only name and host_name'
        columns = {
            "columns[0][data]": "host_name",
            "columns[0][name]": "",
            "columns[0][searchable]": "true",
            "columns[0][orderable]": "true",
            "columns[0][search][value]": "",
            "columns[0][search][regexp]": "false",
            "columns[1][data]": "host_name",
            "columns[1][name]": "",
            "columns[1][searchable]": "true",
            "columns[1][orderable]": "true",
            "columns[1][search][value]": "",
            "columns[1][search][regexp]": "false",
        }
        parameters = { 'length': 2 }
        parameters.update(columns)
        print "parameters: ", parameters
        rv = self.app.get('/hosts/data', query_string=parameters)
        print "Status: %d, '%s'" % (rv.status_code, rv.status)
        ok_(rv.status_code == 200)
        ok_(rv.status == '200 OK')
        ok_(rv.data)
        print "Data: %s" % (rv.data)
        json_data = json.loads(rv.data)
        print "JSON Data: %s" % (json_data)
        ok_('recordsTotal' in json_data)
        ok_('recordsFiltered' in json_data)
        ok_('draw' in json_data)
        ok_('data' in json_data)
        i = 0
        for line in json_data['data']:
            print line['host_name']
            i = i + 1
        ok_(i == 2)
