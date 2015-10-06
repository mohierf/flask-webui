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
    ``alignak_webui.user`` module

    Application user
"""

from logging import getLogger
from datetime import datetime
from flask_login import UserMixin
from alignak_webui import app, manifest

logger = getLogger(__name__)


# Simple user class based on UserMixin
# http://flask-login.readthedocs.org/en/latest/_modules/flask/ext/login.html#UserMixin
class User(UserMixin):
    """
        User class inherited from UserMixin
        (https://flask-login.readthedocs.org/en/latest/_modules/flask_login.html#UserMixin)

    """
    backend = None
    token = None
    username = None
    password = None

    def __init__(self):
        """Create a user"""
        self.contact = None
        self.picture = None
        self.name = None
        self.role = None
        self.is_validated = False

    def __str__(self):
        """User to String"""
        return "%s (%s)" % (self.get_username(), self.get_role())

    @classmethod
    def set_backend(cls, backend):
        """
        Set the backend used to authenticate users
        """
        cls.backend = backend
        logger.debug("users' authentication backend defined: %s", backend.url_endpoint_root)

    @classmethod
    def get_from_username(cls, username):  # pragma: no cover - impossible in unit testing
        """
            Return user instance for the provided username

            Returns None if not exist
        """
        logger.debug("Get user from username: %s", username)
        if cls.username == username:
            logger.debug("get_from_username, user is already initialized")
            return cls
        else:
            user = User()
            parameters = {"where": '{"contact_name": "%s"}' % username}
            if user.get_from_backend(parameters):
                user.is_validated = True
                return user

        return None

    @classmethod
    def get_from_token(cls, token):  # pragma: no cover - impossible in unit testing
        """
            Return user instance for the provided token

            Returns None if not exist
        """
        logger.debug("Get user from token: %s", token)
        if cls.token == token:
            logger.debug("get_from_token, user is already initialized")
            return cls
        else:
            user = User()
            if user.authenticate(token=token):
                user.is_validated = True
                return user

        logger.error(" Backend connection failed")
        return None

    def get_from_backend(self, search_pattern):
        """
            Get user information available in the backend

            search_pattern is an Eve filter expression:
            - {"where": '{"contact_name": "admin"}'}
            - {"where": '{"token": "Abcdefghijk"}'}

            Returns False if information are not available

            :param label: search_pattern
            :type label: dict

            :return: True / False
            :rtype: bool
        """
        try:
            logger.debug("Request matching contacts from backend ...")
            contacts = self.backend.get_objects(
                'contact', parameters=search_pattern, all_elements=True
            )
            logger.debug("Got %d matching contacts", len(contacts))
            if contacts:
                self.contact = {}
                for key in contacts[0]:
                    logger.debug("Add attribute '%s' = %s", key, contacts[0][key])
                    self.contact[key] = contacts[0][key]

                self.username = self.contact['contact_name'] or None
                self.password = self.contact['back_password'] or None

                self.name = 'unknown'
                if 'name' in self.contact and self.contact["name"]:
                    self.name = self.contact["name"]
                elif 'alias' in self.contact and self.contact["alias"]:
                    self.name = self.contact["alias"]

                self.role = 'user'
                if 'role' in self.contact and self.contact["role"]:
                    self.role = app.config.get('users.role_' + self.contact["role"], self.role)
                elif self.contact["back_role_super_admin"]:
                    self.role = 'super_admin'
                elif self.contact["back_role_admin"]:
                    self.role = 'admin'

                self.picture = "/static/images/default_user.png"
                if 'picture' in self.contact and self.contact["picture"]:
                    self.picture = app.config.get('users.picture_' + self.role, self.picture)

                logger.debug("User initialized from backend contact, username: %s", self.username)
                return True
        except Exception as e:  # pragma: no cover - should never happen
            logger.error("Backend raised an exception: %s.", str(e))

        return False

    def get_id(self):
        """
            Return user identifier

            Returns None if not exist
        """
        return self.get_username()

    def authenticate(self, username=None, password=None, token=None):
        """
            Authenticate user with provided username and password

            Try to log in to the defined backend

            :param username: username
            :type username: string

            :param password: password
            :type password: string

            :return: True / False
            :rtype: bool
        """

        logger.debug("User authenticating, credentials: %s/%s", username, token)
        self.is_validated = False
        try:
            if token:
                self.token = self.backend.login(token=token)
            else:
                self.token = self.backend.login(username=username, password=password)
            logger.debug("User authentication, token: %s", self.token)
        except Exception as e:
            logger.error("Backend raised an exception: %s.", str(e))
        else:
            if self.token:
                self.get_from_backend({"where": '{"token": "%s"}' % self.token})

                logger.debug("User is authenticated, username: %s", username)

                if self.backend.connect(token=self.token):
                    self.is_validated = True
                    return self.is_validated
                else:
                    logger.error(" Backend connection failed")

        self.username = None
        self.password = None
        self.token = None
        self.contact = None
        return self.is_validated

    def get_auth_token(self):
        """ ...
        :return: token
        :rtype: string
        """
        return self.token

    def get_username(self):
        """ ...
        :return: username
        :rtype: string
        """

        return self.username

    def get_name(self):
        """Returns a friendly name if exists, else username

        :return: name
        :rtype: string
        """
        return self.name

    def get_role(self):
        """Returns a role name ... defined in application config.

        :return: user's role
        :rtype: string
        """

        return self.role

    def get_picture(self):
        """Returns an URL of user picture

        :return: user's picture URL
        :rtype: string
        """

        return self.picture

    def can_admin(self):
        """If user is an administrator

        :return: user ability to act on the system
        :rtype: boolean
        """

        return self.get_role() == 'super_admin' or self.get_role() == 'admin'

    def can_action(self):
        """If user can submit some actions ...

        :return: user ability to act on the system
        :rtype: boolean
        """

        if "can_submit_commands" in self.contact:
            return self.contact["can_submit_commands"] == '1'
        else:
            return self.can_admin()
