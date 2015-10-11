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

from alignak_webui import app, frontend
from alignak_webui.datatable import Datatable, DatatableException
from flask import Blueprint, jsonify, render_template
from flask_login import login_required
from flask_classy import FlaskView, route
from logging import getLogger


logger = getLogger(__name__)


class ElementsView(FlaskView):
    """ Generice class for an element stored in the backend """
    object_type = "unknown"
    element_table = None
    parameters = {
        'max_results': 1
    }

    @route('get_prefs', methods=['GET'])
    @login_required
    def get_prefs(self):
        """ Call default datatables function """
        return self.element_table.get_prefs()

    @route('set_prefs', methods=['POST'])
    @login_required
    def set_prefs(self):
        """ Call default datatables function """
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
        logger.debug("ElementsView, get: %s", name)

        # Update default parameters ...
        self.parameters['where'] = '{"host_name":"%s"}' % name

        resp = frontend.get_objects(self.object_type, parameters=self.parameters)
        logger.debug("ElementsView, response: %s", resp)
        if not '_items' in resp:
            # Not found
            logger.warning("HostsView, host: %s does not exist.", name)

            return render_template(
                'element.html',
                object_type=self.object_type,
                columns=None,
                object=None
            )
        else:
            fields = frontend.get_ui_data_model(self.object_type)
            if not fields:
                raise DatatableException(450, "table, trying to get table data for unmanaged data")

            table_columns = []
            # Objects are considered in the UI
            for field in fields:
                if field["name"] == "ui":
                    continue

                if 'ui' in field and 'visible' in field['ui'] and field["ui"]["visible"]:
                    # Ensuring data model is clean will avoid those tests ...
                    field_default = ""
                    if 'default' in field:
                        field_default = field["default"]
                    field_title = field["name"]
                    if 'title' in field['ui']:
                        field_title = field["ui"]["title"]
                    table_columns.append({
                        "name": field["name"],
                        "title": field_title,
                        "defaultContent": field_default,
                        "type": field['type'],
                        "orderable": field["ui"]["orderable"],
                        "searchable": field["ui"]["searchable"],
                        "data": field['name']
                    })

        return render_template(
            'element.html',
            object_type=self.object_type,
            columns=table_columns,
            object=resp['_items'][0]
        )
