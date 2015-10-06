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

from alignak_webui import app
from alignak_webui.datatable import Datatable
from alignak_webui.element import ElementsView
from flask import Blueprint
from logging import getLogger


logger = getLogger(__name__)

# Plugin name
PLUGIN_NAME = "services"

# Flask Blueprint object
bp_name = Blueprint(PLUGIN_NAME, __name__, template_folder='templates', static_folder='static')


class ServicesView(ElementsView):
    """ Backend service object """

    def __init__(self):
        """Create a new element"""
        # Call the base class constructor with the parameters it needs
        super(ServicesView, self).__init__()
        self.object_type = "service"
        self.element_table = Datatable(self.object_type)


# Register view class near Flask application
ServicesView().register(app, trailing_slash=False)
