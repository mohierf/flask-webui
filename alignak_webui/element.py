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
from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required
from flask_classy import FlaskView, route
from logging import getLogger


logger = getLogger(__name__)


from wtforms import Form, validators
from wtforms import IntegerField, BooleanField, FloatField, StringField, SelectField

class ElementForm(Form):
    @classmethod
    def append_field(cls, name, field):
        setattr(cls, name, field)
        return cls


class ElementsView(FlaskView):
    """ Generice class for an element stored in the backend """
    object_type = "unknown"
    element_table = None
    edit_form = None
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

            # Create form dynamically
            class F(Form):
                pass

            table_columns = []
            # Objects are considered in the UI
            for field in fields:
                if field["name"] == "ui":
                    continue
                if not 'ui' in field:
                    continue
                if not 'visible' in field['ui']:
                    continue
                if not field["ui"]["visible"]:
                    continue

                # Ensuring data model is clean will avoid those tests ...
                field_default = ""
                if 'default' in field:
                    field_default = field["default"]
                field_title = field["name"]
                if 'title' in field["ui"]:
                    field_title = field["ui"]["title"]
                table_columns.append({
                    "name": field["name"],
                    "title": field_title,
                    "defaultContent": field_default,
                    "type": field["type"],
                    "format": field["ui"]["format"],
                    "orderable": field["ui"]["orderable"],
                    "searchable": field["ui"]["searchable"],
                    "data": field['name']
                })
                # Update form dynamically
                form_field = None
                valids = []
                if field["required"]:
                    valids.append(validators.InputRequired())

                if field["type"] == 'objectid':
                    logger.debug("ElementsView, field '%s' type: %s", field["name"], field["type"])
                    form_field = StringField(
                        label="Link to "+field_title,
                        description=field_title,
                        default=field_default,
                        validators=valids
                    )
                elif field["type"] == 'string':
                    logger.debug("ElementsView, field '%s' type: %s", field["name"], field["type"])
                    form_field = StringField(
                        label=field_title,
                        description=field_title,
                        default=field_default,
                        validators=valids
                    )
                elif field["type"] == 'boolean':
                    logger.debug("ElementsView, field '%s' type: %s", field["name"], field["type"])
                    form_field = BooleanField(
                        label=field_title,
                        description=field_title,
                        default=field_default,
                        validators=valids
                    )
                elif field["type"] == 'integer':
                    logger.debug("ElementsView, field '%s' type: %s", field["name"], field["type"])
                    form_field = IntegerField(
                        label=field_title,
                        description=field_title,
                        default=field_default,
                        validators=valids
                    )
                elif field["type"] == 'float':
                    logger.debug("ElementsView, field '%s' type: %s", field["name"], field["type"])
                    form_field = FloatField(
                        label=field_title,
                        description=field_title,
                        default=field_default,
                        validators=valids
                    )
                elif field["type"] == 'list':
                    logger.debug("ElementsView, field '%s' type: %s", field["name"], field["type"])
                    choices=[]
                    if "allowed" in field and field["allowed"]:
                        field["ui"]["format"] = {
                            "list_allowed": {
                                u"d": u"Down",
                                u"u": u"Up",
                                u"r": u"Recovery",
                                u"f": u"Flapping",
                                u"s": u"Downtime",
                                u"o": u"Downtime",
                                u"w": u"Warning",
                                u"n": u"None",
                                u"c": u"Critical",
                            }
                        }
                        if "list_allowed" in field["ui"]["format"]:
                            for choice in field["allowed"]:
                                choices.append( (choice, field["ui"]["format"]["list_allowed"][choice]))

                    form_field = SelectField(
                        label=field_title,
                        description=field_title,
                        default=field_default,
                        choices=choices,
                        validators=valids
                    )
                else:
                    logger.debug("ElementsView, field '%s' unspecified type", field["name"])
                    form_field = StringField(
                        label=field_title,
                        description=field_title,
                        default=field_default,
                        validators=valids
                    )

                # Fields may also be Date, DateTime, Decimal, File, Radio, Select, SelectMultiple

                setattr(
                    F,
                    field['name'],
                    form_field
                )

        # Current object
        object=resp['_items'][0]

        self.edit_form = F(request.form, obj=None, **object)
        logger.debug("ElementsView, form: %s", self.edit_form)
        logger.debug("ElementsView, form data: %s", self.edit_form.data)

        return render_template(
            '%s.html' % self.object_type,
            object_type=self.object_type,
            columns=table_columns,
            object=resp['_items'][0],
            form=self.edit_form
        )
