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
    ``alignak_webui.plugins.services`` module

    Services application functions

    List of services
    -------------------

    Service page
    ------------------------
"""

from alignak_webui.datatable import set_prefs, get_prefs, table_data, table, page
from flask import Blueprint
from flask_login import login_required
from logging import getLogger

logger = getLogger(__name__)

# Plugin name
PLUGIN_NAME = "services"
OBJECT_TYPE = "service"

# Flask Blueprint object
services = Blueprint('services', __name__, template_folder='templates', static_folder='static')


@services.route('/get_prefs')
@login_required
def services_get_prefs():
    """ Call default datatables function """
    logger.debug("services_get_prefs")

    response = get_prefs(OBJECT_TYPE)
    logger.debug("services_get_prefs, response: %s", response)
    return response


@services.route('/set_prefs', methods=['POST'])
@login_required
def services_set_prefs():
    """ Call default datatables function """
    logger.debug("services_set_prefs")
    return set_prefs(OBJECT_TYPE)


@services.route('/data')
@login_required
def services_data():
    """ Call default datatables function """
    return table_data(OBJECT_TYPE)


@services.route('')
@login_required
def services_list():
    """ Call default datatables function """
    return table(OBJECT_TYPE)


@services.route('/<name>')
@login_required
def services_page(name):
    """ Call default datatables function """
    logger.debug("services_page: %s", name)

    return page(OBJECT_TYPE)
