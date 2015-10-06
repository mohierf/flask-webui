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
    ``alignak_webui.element`` module

    Element application functions

    List of elements
    -------------------

    Element page
    ------------------------
"""

from alignak_webui import app
from alignak_webui.datatable import Datatable
from flask import Blueprint
from flask_login import login_required
from flask_classy import FlaskView, route
from logging import getLogger


logger = getLogger(__name__)


class ElementsView(FlaskView):
    """ Generice class for an element stored in the backend """
    object_type = "unknown"
    element_table = None

    @route('get_prefs', methods=['GET'])
    @login_required
    def get_prefs(self):
        """ Call default datatables function """
        logger.debug("get_prefs")

        response = self.element_table.get_prefs()
        logger.debug("get_prefs, response: %s", response)
        return response

    @route('set_prefs', methods=['POST'])
    @login_required
    def set_prefs(self):
        """ Call default datatables function """
        logger.debug("set_prefs")
        return self.element_table.set_prefs()

    @route('data', methods=['GET'])
    @login_required
    def data(self):
        """ Call default datatables function """
        return self.element_table.table_data()

    @login_required
    def index(self):
        """ Call default datatables function """
        return self.element_table.table()

    @login_required
    def get(self, name):
        """ Call default datatables function """
        logger.debug("page: %s", name)

        return self.element_table.page()
