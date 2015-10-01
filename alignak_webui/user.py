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
from logging import getLogger
from datetime import datetime
from flask.ext.login import UserMixin

log = getLogger(__name__)


# Simple user class based on UserMixin
# http://flask-login.readthedocs.org/en/latest/_modules/flask/ext/login.html#UserMixin
class UserNotFoundError(Exception):
    pass

class NoBackendError(Exception):
    pass

class User(UserMixin):
    """
        User class inherited from UserMixin
        (https://flask-login.readthedocs.org/en/latest/_modules/flask_login.html#UserMixin)

    """
    backend = None
    token = None
    username = None
    # password = None

    def __init__(self):
        self.contact = None

    @classmethod
    def set_backend(cls, backend):
        """
        Set the backend used to authenticate users
        """
        cls.backend = backend
        log.debug("users' authentication backend defined: %s", backend.url_endpoint_root)

    def get_id(self):
        """
            Return user identifier

            Returns None if not exist
        """
        return self.username

    @classmethod
    def get_from_username(cls, username):
        """
            Return user instance for the provided username

            Returns None if not exist
        """
        log.debug("Get user from username: %s", username)
        if cls.username == username:
            return cls
        else:
            log.debug("Request matching contacts from backend ...")
            parameters = {"where": '{"contact_name": "%s"}' % username}
            contacts = cls.backend.get_objects('contact', parameters=parameters, all_elements=True)
            log.debug("Got %d matching contacts", len(contacts))
            if contacts:
                cls.contact = {}
                for key in contacts[0]:
                    log.debug("Add %s attribute, value is: %s", key, contacts[0][key])
                    cls.contact[key] = contacts[0][key]

                cls.username = username
                # cls.password = password
                log.debug("User is initialized from backend contact, username: %s", username)
                return cls

            return None

    @classmethod
    def get_from_token(cls, token):
        """
            Return user instance for the provided token

            Returns None if not exist
        """
        log.debug("Get user from token: %s", token)
        if cls.token == token:
            return cls
        else:
            log.debug("Request matching contacts from backend ...")
            parameters = {"where": '{"token": "%s"}' % token}
            contacts = cls.backend.get_objects('contact', parameters=parameters, all_elements=True)
            log.debug("Got %d matching contacts", len(contacts))
            if contacts:
                cls.contact = {}
                for key in contacts[0]:
                    log.debug("Add %s attribute, value is: %s", key, contacts[0][key])
                    cls.contact[key] = contacts[0][key]

                cls.token = token
                # cls.password = password
                log.debug("User is initialized from backend contact, token: %s", token)
                return cls

            return None

    def authenticate(self, username, password):
        global frontend
        log.debug("User authenticating, credentials: %s/%s", username, password)
        try:
            self.token = self.backend.login(username, password, force=True)
            log.debug("User authentication, token: %s", self.token)
        except Exception:
            log.error("Backend error")
            raise NoBackendError()

        log.debug("User is authenticated, username: %s", username)
        if self.token:
            if self.get_from_username(username):
                return True
            # parameters = {"where": '{"contact_name": "%s"}' % username}
            # contacts = self.backend.get_objects('contact', parameters=parameters, all_elements=True)
            # log.debug("Got %d contacts matching username", len(contacts))
            # if contacts:
                # self.contact = {}
                # for key in contacts[0]:
                    # log.debug("Add %s attribute", key)
                    # self.contact[key] = contacts[0][key]

                # self.username = username
                # self.password = password
                # log.debug("User is initialized from backend contact, username: %s", username)
            # return True

        self.username = None
        self.password = None
        self.contact = None
        return False

    def get_auth_token(self):
        return self.get_id()
