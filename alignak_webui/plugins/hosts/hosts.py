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
    ``alignak_webui.plugins.hosts`` module

    Hosts application functions

    List of hosts
    -------------------

    Host page
    ------------------------
"""

from alignak_webui import app, frontend
from alignak_webui.datatable import Datatable, DatatableException
from alignak_webui.element import ElementsView
from flask import Blueprint, jsonify, render_template
from flask_login import login_required
from logging import getLogger


logger = getLogger(__name__)

# Plugin name
PLUGIN_NAME = "hosts"

# Flask Blueprint object
bp_name = Blueprint(PLUGIN_NAME, __name__, template_folder='templates', static_folder='static')


class HostsView(ElementsView):
    """ Backend host object """

    parameters = {
        'max_results': 1,
        'embedded':
            '{'\
                '"hostgroups": 1, '\
                '"contacts": 1,'\
                '"check_period": 1,'\
                '"notification_period": 1,'\
                '"check_command": 1'\
            '}'
    }

    def __init__(self):
        """Create a new element"""
        # Call the base class constructor with the parameters it needs
        super(HostsView, self).__init__()
        self.object_type = "host"
        self.element_table = Datatable(self.object_type)

    @login_required
    def get(self, name):
        """ Call default ElementsView class function """
        logger.debug("HostsView, get: %s", name)
        return super(HostsView, self).get(name)


# Register view class near Flask application
HostsView().register(app, trailing_slash=False)
