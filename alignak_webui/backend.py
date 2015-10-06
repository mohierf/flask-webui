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
    ``alignak_webui.backend`` module

    Interface to the Alignak backend

"""

import os
import time
import re
import traceback
import logging

import json

# Import specific modules
import requests
# from requests import *
from requests.auth import HTTPBasicAuth

# import alignak_backend_client.client
from alignak_backend_client.client import Backend, BackendException

log = logging.getLogger(__name__)


class FrontEnd(object):
    """
    Frontend class used to communicate with alignak-backend
    """
    last_livestate_hosts = None
    last_livestate_services = None

    def __init__(self):
        """
        Initialize class object ...
        """
        self.url_endpoint_root = None
        self.backend = None

        self.connected = False
        self.initialized = False
        self.authenticated = False
        self.token = None

        # Backend objects which will be loaded on backend connection ...
        # ... do not need to wait for any user request to get these objects
        self.interested_in = ['contact', 'uipref']

        # Backend available objects (filled with objects received from backend)
        self.backend_available_objets = []

        # Frontend objects
        self.objects_cache = {}

        # API Data model
        self.dm_server_name = None
        self.dm_api_name = None
        self.dm_base = None
        self.dm_domains = {}

    def configure(self, endpoint):
        """
        Initialize backend connection ...
        """
        # Backend API start point
        if endpoint.endswith('/'):  # pragma: no cover - test url is complying ...
            self.url_endpoint_root = endpoint[0:-1]
        else:
            self.url_endpoint_root = endpoint

        log.info("backend endpoint: %s", self.url_endpoint_root)
        self.backend = Backend(self.url_endpoint_root)

    def login(self, username=None, password=None, token=None, force=False):
        """
        Authenticate user credentials against backend

        :param username: user to authenticate
        :type username: string
        :param password: password
        :type password: string
        :return: user token if authenticated, else None
        :rtype: string
        """
        try:
            if self.authenticated and self.token and not force:
                return self.token

            if token:
                try:
                    # Test the backend connection
                    self.backend.token = token
                    log.info("request backend user authentication, token: %s", token)
                    self.backend_available_objets = self.backend.get_domains()
                    if self.backend_available_objets:
                        self.authenticated = True
                        self.token = token
                        log.info("backend user authenticated")
                except BackendException as e:
                    log.error("frontend connection, error: %s", str(e))
                    self.authenticated = False
                    self.token = None
            else:
                self.authenticated = False
                self.token = None
                log.info("request backend user authentication, username: %s", username)
                self.authenticated = self.backend.login(username=username, password=password)
                if self.authenticated:
                    self.token = self.backend.token

                    log.info("backend user authenticated: %s", username)
        except BackendException as e:
            log.error("backend login, error: %s", str(e))
            log.debug("exception type: %s", type(e))
            log.debug("Back trace of this kill: %s", traceback.format_exc())
            self.connected = False
            self.authenticated = self.connected
            raise e

        return self.token

    def logout(self):
        """
        Logout user from backend

        :return: True
        :rtype: boolean
        """
        self.connected = False
        self.authenticated = False
        self.token = None

        return self.backend.logout()

    def connect(self, username=None, token=None):
        """
        If backend connection is available:
        - retrieves all managed domains on the root endpoint
        - get the backend schema (models)
        - load some persistent elements (defined on init)
        - find the contact associated with the current logged in user

        :param username: authenticated user
        :type username: string
        :param token: user token
        :type token: string
        :return: true / false
        :rtype: boolean
        """
        try:
            self.connected = False
            matching_contact = False

            # Backend authentication ...
            if not self.authenticated:
                return self.connected

            # Connect the backend
            self.backend_available_objets = self.backend.get_domains()
            if self.backend_available_objets:
                self.connected = True

            if self.connected:
                # Retrieve data model from the backend
                response = requests.get('/'.join([self.url_endpoint_root, 'docs/spec.json']))
                resp = response.json()
                self.dm_server_name = resp['server_name']
                self.dm_api_name = resp['api_name']
                self.dm_base = resp['base']
                self.dm_domains = {}
                for domain_name in resp['domains']:
                    fields = resp['domains'][domain_name]["/" + domain_name]['POST']['params']
                    self.dm_domains.update({
                        domain_name: fields
                    })

                # Initialize embedded objects
                if not self.initialized:
                    self.initialize()

                # If we got contacts, try to find a contact matching our authenticated user ...
                if 'contact' in self.objects_cache:
                    for contact in self.objects_cache['contact']:
                        log.debug(
                            "available contact: %s / %s", contact["contact_name"], contact["token"]
                        )
                        if (token and contact["token"] == token) or (
                                username and contact["contact_name"] == username):
                            matching_contact = True
                            # contact["_token"] = self.token
                            log.info(
                                "found a contact matching logged in user contact: %s",
                                contact["contact_name"]
                            )
                    self.connected = matching_contact
                    self.authenticated = self.connected

        except BackendException as e:
            log.error("frontend connection, error: %s", str(e))
            self.connected = False
            self.authenticated = self.connected
            raise e
        except Exception as e:  # pragma: no cover - simple protection if ever happened ...
            log.error("frontend connection, error: %s", str(e))
            log.debug("exception type: %s", type(e))
            log.debug("Back trace of this kill: %s", traceback.format_exc())

        return self.connected

    def disconnect(self):
        """
        Disconnect backend

        :return: True
        :rtype: boolean
        """
        self.connected = False
        self.authenticated = False
        self.token = None

        self.backend.logout()

        return True

    def initialize(self):
        """
        Initialize self cached backend objects.

        Load the backend that we will keep in our cache.

        :return: true / false
        :rtype: boolean
        """
        try:
            self.initialized = False

            # Connect to backend if not yet connected ...
            if not self.connected:  # pragma: no cover - simple protection if ever happened ...
                self.connected = self.connect()

            if not self.connected:  # pragma: no cover - simple protection if ever happened ...
                return False

            # Fetch only objects type which I am interested in ...
            for object_type in self.backend_available_objets:
                t = object_type["href"]
                if t in self.interested_in:
                    log.info(
                        "getting '%s' cached objects on %s%s",
                        object_type["title"], self.url_endpoint_root, t
                    )

                    # Get all objects of type t ...
                    items = self.get_objects(t, None, True)

                    self.objects_cache[t] = items

            self.initialized = True
        except Exception as e:  # pragma: no cover
            log.error("FrontEnd, initialize, exception: %s", str(e))

        return self.initialized

    def get_objects(self, object_type, parameters=None, all_elements=False):
        """
        Get stored objects

        !!! NOTE !!!
        Beware of the all_elements=True parameter because the backend client method fetches all
        the elements and the get_objects is not able anymore to send the _meta information !

        :param object_type: object type (eg. host, contact, ...)
        :type object_type: str
        :param parameters: list of parameters for the backend API
        :type parameters: list
        :return: list of properties when query item | list of items when get many items
        :rtype: list
        """
        try:
            items = []

            log.info("get_objects, type: %s, parameters: %s / %d",
                     object_type, parameters, all_elements)

            # Request objects from the backend ...
            if all_elements:
                items = self.backend.get_all(object_type, parameters)
            else:
                items = self.backend.get(object_type, parameters)
            # log.debug("get_objects, type: %s, items: %s", object_type, items)

            # Should be handled in the try / except ... but exception is not always raised!
            if '_error' in items:  # pragma: no cover - need specific backend tests
                error = items['_error']
                log.error(
                    "backend get: %s, %s",
                    error['code'], error['message']
                )
                items = []

        except Exception as e:  # pragma: no cover - need specific backend tests
            log.error("get_objects, exception: %s", str(e))

        return items

    def set_user_preferences(self, user, prefs_type, parameters):
        """
        Set user's preferences

        An exception is raised if an error occurs, else returns the backend response

        :param user: username
        :type user: str
        :param prefs_type: preference type
        :type prefs_type: str
        :param parameters: list of parameters for the backend API
        :type parameters: list
        :return: server's response
        :rtype: dict
        """
        try:
            response = None

            log.debug("set_user_preferences, type: %s, for: %s, parameters: %s",
                      prefs_type, user, parameters)

            # Still existing ...
            items = self.backend.get_all(
                'uipref',
                params={'where': '{"type":"%s", "user": "%s"}' % (prefs_type, user)}
            )
            if items:
                items = items[0]
                log.info(
                    "set_user_preferences, update exising record: %s / %s (%s)",
                    prefs_type, user, items['_id']
                )
                # Update existing record ...
                headers = {'If-Match': items['_etag']}
                data = {
                    "user": user,
                    "type": prefs_type,
                    "data": parameters
                }
                response = self.backend.patch(
                    '/'.join(['uipref', items['_id']]),
                    data=data, headers=headers, inception=True
                )
            else:
                # Create new record ...
                log.info(
                    "set_user_preferences, create new record: %s / %s",
                    prefs_type, user
                )
                data = {
                    "user": user,
                    "type": prefs_type,
                    "data": parameters
                }
                response = self.backend.post('uipref', data=data)
            log.debug("set_user_preferences, response: %s", response)

        except Exception as e:  # pragma: no cover - need specific backend tests
            log.error("set_user_preferences, exception: %s", str(e))
            raise e

        return response

    def get_user_preferences(self, user, prefs_type):
        """
        Get user's preferences

        If the data are not found, returns None else return found data.

        :param user: username
        :type user: str
        :param prefs_type: preference type
        :type prefs_type: str
        :return: found data, or None
        :rtype: dict
        """
        try:
            log.debug("get_user_preferences, type: %s, for: %s", prefs_type, user)

            # Still existing ...
            items = self.backend.get_all(
                'uipref',
                params={'where': '{"type":"%s", "user": "%s"}' % (prefs_type, user)}
            )
            if items:
                log.debug("get_user_preferences, found: %s", items[0])
                return items[0]

        except Exception as e:  # pragma: no cover - need specific backend tests
            log.error("get_user_preferences, exception: %s", str(e))
            raise e

        return None  # pragma: no cover - need specific backend tests

    def get_ui_data_model(self, element_type):
        """ Get the data model for an element type

            If the data model specifies that the element is managed in the UI,
            all the fields for this element are provided

            :param element_type: element type
            :type element_type: str
            :return: list of fields name/title
            :rtype: list
        """
        log.debug("get_ui_data_model, element type: %s", element_type)
        log.debug("get_ui_data_model, domains: %s", self.dm_domains)

        fields = []
        if element_type in self.dm_domains:
            for model in self.dm_domains[element_type]:
                log.debug("get_ui_data_model, model: %s", model["name"])
                # element is considered for the UI
                if 'ui' in model["name"]:
                    fields = self.dm_domains[element_type]
                    break
        return fields

    def get_livestate(self, parameters=None):
        """ Get livestate for hosts and services

            :return: list of hosts/services live states
            :rtype: list
        """
        return self.get_objects('livestate', parameters)

    def get_livestate_hosts(self, parameters=None):
        """ Get livestate for hosts

            Elements in the livestat which service_description is null

            :return: list of hosts live states
            :rtype: list
        """
        if not parameters:
            parameters = {}
        parameters.update({'where': '{"service_description": null}'})
        return self.get_objects('livestate', parameters, all_elements=True)

    def get_livestate_services(self, parameters=None):
        """ Get livestate for services

            Elements in the livestat which service_description is not null

            :return: list of services live states
            :rtype: list
        """
        if not parameters:
            parameters = {}
        parameters.update({'where': '{"service_description": {"$ne": null}}'})
        return self.get_objects('livestate', parameters, all_elements=True)

    def search_hosts_and_services(self, search, sorter=None):
        """ Search hosts and services.

            This method is the heart of the datamanager. All other methods should be
            based on this one.

            :param search: Search string
            :type search: str
            :param get_impacts: should impacts be included in the list?
            :type get_impacts: boolean
            :param sorter: function to sort the items. default=None (means no sorting)
            :type sorter: function
            :return: list of hosts and services
            :rtype: list
        """
        items = []
        items.extend(self.get_objects('host'), all=True)
        items.extend(self.get_objects('service'), all=True)

        search = [s for s in search.split(' ')]

        for s in search:
            s = s.strip()
            if not s:
                continue

            elts = s.split(':', 1)
            t = 'hst_srv'
            if len(elts) > 1:
                t = elts[0]
                s = elts[1]

            s = s.lower()
            t = t.lower()

            if t == 'hst_srv':
                pat = re.compile(s, re.IGNORECASE)
                new_items = []
                for i in items:
                    if pat.search(i.get_full_name()):
                        new_items.append(i)
                    else:
                        for j in i.impacts + i.source_problems:
                            if pat.search(j.get_full_name()):
                                new_items.append(i)

                if not new_items:
                    for i in items:
                        if pat.search(i.output):
                            new_items.append(i)
                        else:
                            for j in i.impacts + i.source_problems:
                                if pat.search(j.output):
                                    new_items.append(i)

                items = new_items

            if t == 'type' and s != 'all':
                items = [i for i in items if i.__class__.my_type == s]

            if t == 'bp' or t == 'bi':
                if s.startswith('>='):
                    items = [i for i in items if i.business_impact >= int(s[2:])]
                elif s.startswith('<='):
                    items = [i for i in items if i.business_impact <= int(s[2:])]
                elif s.startswith('>'):
                    items = [i for i in items if i.business_impact > int(s[1:])]
                elif s.startswith('<'):
                    items = [i for i in items if i.business_impact < int(s[1:])]
                else:
                    if s.startswith('='):
                        s = s[1:]
                    items = [i for i in items if i.business_impact == int(s)]

            if t == 'duration':
                seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
                times = [(i, time.time() - int(i.last_state_change)) for i in items]
                try:
                    if s.startswith('>='):
                        s = int(s[2:-1]) * seconds_per_unit[s[-1].lower()]
                        items = [i[0] for i in times if i[1] >= s]
                    elif s.startswith('<='):
                        s = int(s[2:-1]) * seconds_per_unit[s[-1].lower()]
                        items = [i[0] for i in times if i[1] <= s]
                    elif s.startswith('>'):
                        s = int(s[1:-1]) * seconds_per_unit[s[-1].lower()]
                        items = [i[0] for i in times if i[1] > s]
                    elif s.startswith('<'):
                        s = int(s[1:-1]) * seconds_per_unit[s[-1].lower()]
                        items = [i[0] for i in times if i[1] < s]
                    else:
                        items = []
                except Exception:
                    items = []

            if t == 'is':
                if s.lower() == 'ack':
                    items = [i for i in items if (i.__class__.my_type == 'service' or
                                                  i.problem_has_been_acknowledged)]
                    items = [i for i in items if (i.__class__.my_type == 'host' or
                                                  (i.problem_has_been_acknowledged or
                                                   i.host.problem_has_been_acknowledged))]
                elif s.lower() == 'downtime':
                    items = [i for i in items if (i.__class__.my_type == 'service' or
                                                  i.in_scheduled_downtime)]
                    items = [i for i in items if (i.__class__.my_type == 'host' or
                                                  (i.in_scheduled_downtime or
                                                   i.host.in_scheduled_downtime))]
                elif s.lower() == 'impact':
                    items = [i for i in items if i.is_impact]
                else:
                    if len(s) == 1:
                        items = [i for i in items if i.state_id == int(s)]
                    else:
                        items = [i for i in items if i.state == s.upper()]

            if t == 'isnot':
                if s.lower() == 'ack':
                    items = [i for i in items if (i.__class__.my_type == 'service' or
                                                  not i.problem_has_been_acknowledged)]
                    items = [i for i in items if (i.__class__.my_type == 'host' or
                                                  (not i.problem_has_been_acknowledged and
                                                   not i.host.problem_has_been_acknowledged))]
                elif s.lower() == 'downtime':
                    items = [i for i in items if (i.__class__.my_type == 'service' or
                                                  not i.in_scheduled_downtime)]
                    items = [i for i in items if (i.__class__.my_type == 'host' or
                                                  (not i.in_scheduled_downtime and
                                                   not i.host.in_scheduled_downtime))]
                elif s.lower() == 'impact':
                    items = [i for i in items if not i.is_impact]
                else:
                    if len(s) == 1:
                        items = [i for i in items if i.state_id != int(s)]
                    else:
                        items = [i for i in items if i.state != s.upper()]

            # :COMMENT:maethor:150616: Legacy filters, kept for bookmarks compatibility
            if t == 'ack':
                if s == 'false' or s == 'no':
                    search.append("isnot:ack")
                if s == 'true' or s == 'yes':
                    search.append("is:ack")
            if t == 'downtime':
                if s == 'false' or s == 'no':
                    search.append("isnot:downtime")
                if s == 'true' or s == 'yes':
                    search.append("is:downtime")
            if t == 'crit':
                search.append("is:critical")

        if sorter is not None:
            items.sort(sorter)

        return items

    def get_livesynthesis(self):
        """ Get livestate synthesis for hosts and services

            :return: hosts and services live state synthesis
            :rtype: dict
        """
        synthesis = {
            'hosts_synthesis': self.get_hosts_synthesis(),
            'services_synthesis': self.get_services_synthesis()
        }
        return synthesis

    def get_hosts_synthesis(self):
        """
        @ddurieux: this computation should be made by the backend each time an update occurs!
        Add an API endpoint /hosts_synthesis
        --------------------------------------------------------------------------------------------
        Returns an hosts live state synthesis containing:
            {'nb_down': 4, 'pct_up': 66.67, 'pct_down': 33.33, 'nb_unreachable': 0,
            'nb_unknown': 0, 'pct_problems': 33.33, 'nb_downtime': 0, 'nb_problems': 4,
            'bi': 3, 'pct_unknown': 0.0, 'nb_ack': 0, 'nb_elts': 12, 'nb_up': 8,
            'nb_pending': 0, 'pct_ack': 0.0, 'pct_pending': 0.0, 'pct_downtime': 0.0,
            'pct_unreachable': 0.0}

        Returns none if no hosts are available

        :return: hosts live state synthesis
        :rtype: dict
        """
        parameters = {}
        parameters["embedded"] = '{"host_name":1}'
        hosts = self.get_livestate_hosts(parameters=parameters)
        if not hosts:
            return None

        h = dict()
        h['nb_elts'] = len(hosts)
        h['bi'] = max(int(i['host_name']['business_impact'])
                      for i in hosts if 'business_impact' in i['host_name'])
        for state in 'up', 'down', 'unreachable', 'pending':
            h[state] = [i for i in hosts if i['state'] == state.upper()]
        h['unknown'] = [i for i in hosts if i['state'].lower()
                        not in ['up', 'down', 'unreachable', 'pending']]
        h['ack'] = [i for i in hosts if i['state'] not in ['UP', 'PENDING'] and
                    ('acknowledged' in i and i['acknowledged'])]
        h['downtime'] = [i for i in hosts if ('in_scheduled_downtime' in i and
                                              i['in_scheduled_downtime'])]
        for state in 'up', 'down', 'unreachable', 'pending', 'unknown', 'ack', 'downtime':
            h['nb_' + state] = len(h[state])
            h['pct_' + state] = 0
            if hosts:
                h['pct_' + state] = round(100.0 * h['nb_' + state] / h['nb_elts'], 2)
            del h[state]
        h['nb_problems'] = h['nb_down'] + h['nb_unreachable'] + h['nb_unknown']
        h['pct_problems'] = 0
        if hosts:
            h['pct_problems'] = round(100.0 * h['nb_problems'] / h['nb_elts'], 2)

        log.info("get_hosts_synthesis: %s, %s", type(h), h)
        return h

    def get_services_synthesis(self):
        """
        @ddurieux: this computation should be made by the backend each time an update occurs!
        Add an API endpoint /services_synthesis
        --------------------------------------------------------------------------------------------
        Returns a services live state synthesis containing:
            {'nb_critical': 4, 'pct_ok': 66.67, 'pct_critical': 33.33, 'nb_warning': 0,
            'nb_unknown': 0, 'pct_problems': 33.33, 'nb_downtime': 0, 'nb_problems': 4,
            'bi': 3, 'pct_unknown': 0.0, 'nb_ack': 0, 'nb_elts': 12, 'nb_ok': 8,
            'nb_pending': 0, 'pct_ack': 0.0, 'pct_pending': 0.0, 'pct_downtime': 0.0,
            'pct_warning': 0.0}

        Returns none if no services are available

        :return: services live state synthesis
        :rtype: dict
        """
        parameters = {}
        parameters["embedded"] = '{"service_description":1}'
        services = self.get_livestate_services(parameters=parameters)
        if not services:
            return None

        s = dict()
        s['nb_elts'] = len(services)
        s['bi'] = max(int(i['service_description']['business_impact'])
                      for i in services if 'business_impact' in i['service_description'])
        for state in 'ok', 'critical', 'warning', 'pending':
            s[state] = [i for i in services if i['state'] == state.upper()]
        s['unknown'] = [i for i in services if i['state'].lower()
                        not in ['ok', 'critical', 'warning', 'pending']]
        s['ack'] = [i for i in services if i['state']
                    not in ['OK', 'PENDING'] and i['acknowledged']]
        s['downtime'] = [i for i in services if i['state']
                         not in ['up', 'pending'] and i['acknowledged']]
        for state in 'ok', 'critical', 'warning', 'unknown', 'pending', 'ack', 'downtime':
            s['nb_' + state] = len(s[state])
            s['pct_' + state] = 0
            if services:
                s['pct_' + state] = round(100.0 * s['nb_' + state] / s['nb_elts'], 2)
            del s[state]
        s['nb_problems'] = s['nb_warning'] + s['nb_critical'] + s['nb_unknown']
        s['pct_problems'] = 0
        if services:
            s['pct_problems'] = round(100.0 * s['nb_problems'] / s['nb_elts'], 2)

        log.info("get_services_synthesis: %s", s)
        return s
