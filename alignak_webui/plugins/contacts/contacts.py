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
    ``alignak_webui.plugins.contacts`` module

    Contacts application functions

    List of contacts
    -------------------

    Contact page
    ------------------------
"""

from alignak_webui.datatable import set_prefs, get_prefs, table_data, table, page
from flask import Blueprint, render_template, abort, current_app
from jinja2 import TemplateNotFound
from logging import getLogger

logger = getLogger(__name__)

# Plugin name
PLUGIN_NAME = "contacts"
OBJECT_TYPE = "contact"

# Flask Blueprint object
contacts = Blueprint('contacts', __name__, template_folder='templates', static_folder='static')


@contacts.route('/get_prefs')
def contacts_get_prefs():
    """ Call default datatables function """
    logger.debug("contacts_get_prefs")

    response = get_prefs(OBJECT_TYPE)
    logger.debug("contacts_get_prefs, response: %s", response)
    return response


@contacts.route('/set_prefs', methods=['POST'])
def contacts_set_prefs():
    """ Call default datatables function """
    logger.debug("contacts_set_prefs")
    return set_prefs(OBJECT_TYPE)


@contacts.route('/data')
def contacts_data():
    """ Call default datatables function """
    return table_data(OBJECT_TYPE)


@contacts.route('')
def contacts_list():
    """ Call default datatables function """
    return table(OBJECT_TYPE)


@contacts.route('/<name>')
def contacts_page(name):
    """ Call default datatables function """
    logger.debug("contacts_page: %s", name)

    return page(OBJECT_TYPE)
