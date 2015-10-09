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
    ``alignak_webui.datatables`` module

    Hosts application page

    List of elemnts
    -------------------

    Element page
    ------------------------
"""
import json
from logging import getLogger
from alignak_webui import app, manifest, frontend
from alignak_webui.utils.helper import helper
from flask import request, abort, make_response, render_template
from flask import jsonify
from flask_login import current_user

logger = getLogger(__name__)


class DatatableException(Exception):
    """Specific backend exception
    Defined error codes:
    - 1000: general exception, message contains more information
    - 1001: backend access denied
    - 1002: backend connection timeout
    - 1003: backend uncatched HTTPError
    - 1004: backend token not provided on login, user is not yet authorized to log in
    - 1005: If-Match header is required for patching an object
    """
    def __init__(self, code, message, response=None):
        """Create a new exception"""
        # Call the base class constructor with the parameters it needs
        super(DatatableException, self).__init__(message)
        self.code = code
        self.message = message
        self.response = response

    def __str__(self):
        """Exception to String"""
        return "Datatble error code %d: %s" % (self.code, self.message)


class Datatable(object):
    """ jQuery  Datatable plugin interface for backend elements """

    def __init__(self, object_type):
        """Create a new datatable"""
        self.object_type = object_type

    def set_prefs(self):
        """
        Save preferences

        Posted data to be saved:
            user: username
            type: preference type
            data: data to be saved

        This function stores preferences to the backend
        """
        logger.debug("set_prefs: %s / %s", request.form['user'], request.form['type'])

        # Update user's preferences to the backend ...
        try:
            resp = frontend.set_user_preferences(
                request.form['user'],
                self.object_type + '-' + request.form['type'],
                json.loads(request.form['data'])
            )
            logger.debug("set_prefs, status: %s", resp)

            res = jsonify(**resp)
            res.status_code = 200
            return res
        except Exception as e:  # pragma: no cover - very difficult with unit testing ...
            logger.error("set_prefs, exception: %s", str(e))
            raise DatatableException(
                450,
                "set_prefs, exception: %s / %s" % (type(e), str(e))
            )

        return None

    def get_prefs(self):
        """
        Load preferences

        Request data:
            user: username
            type: preference type

        This function loads preferences from the backend
        """
        logger.debug("get_prefs ...")

        # Fetch user's preferences from the backend ...
        try:
            resp = frontend.get_user_preferences(
                request.args.get('user', 'common'),
                self.object_type + '-' + request.args.get('type', 'common')
            )
            if resp and 'data' in resp:
                res = jsonify(**resp['data'])
                res.status_code = 200
                return res
            else:
                return ''
        except Exception as e:  # pragma: no cover - very difficult with unit testing ...
            logger.error("get_prefs, exception: %s", str(e))
            raise DatatableException(
                450,
                "get_prefs, exception: %s / %s" % (type(e), str(e))
            )

        return None

    def table_data(self):
        """
        Return elements data in json format as of Datatables SSP protocol
        More info: https://datatables.net/manual/server-side

        Example URL:
        GET /?
        draw=1&
        columns[0][data]=alias&
        columns[0][name]=&
        columns[0][searchable]=true&
        columns[0][orderable]=true&
        columns[0][search][value]=&
        columns[0][search][regex]=false&
         ...
        order[0][column]=0&
        order[0][dir]=asc&
        start=0&
        length=10&
        search[value]=&
        search[regex]=false&

        Request parameters are Json formatted


        Request Parameters:
        - draw, index parameter to be returned in the response

            Pagination:
            - start / length, for pagination

            Searching:
            - search (value or regexp)
                search[value]: Global search value. To be applied to all columns which are
                searchable
                => not implemented.
                search[regex]: true if searh[value] is a regex
                => not implemented.

            Sorting:
            - order[i][column] / order[i][dir]
                index of the columns to order and sort direction (asc/desc)

            Columns:
            - columns[i][data]: Column's data source, as defined by columns.data.
            - columns[i][name]: Column's name, as defined by columns.name.
            - columns[i][searchable]: Flag to indicate if this column is searchable (true).
            - columns[i][orderable]: Flag to indicate if this column is orderable (true).
            - columns[i][search][value]: Search value to apply to this specific column.
            - columns[i][search][regex]: Flag to indicate if the search term for this column is a
            regex.

        Response data:
        - draw

        - recordsTotal: total records, before filtering
            (i.e. total number of records in the database)

        - recordsFiltered: Total records, after filtering
            (i.e. total number of records after filtering has been applied -
            not just the number of records being returned for this page of data).
            !!! NOT YET IMPLEMENTED !!!

        - data: The data to be displayed in the table.
            an array of data source objects, one for each row, which will be used by DataTables.

        - error (optional): Error message if an error occurs
            Not included if there is no error.
        """
        logger.info("request for backend data ...")

        # Manage request parameters ...
        # Because of specific datatables parameters name (eg. columns[0] ...)
        # ... some parameters have been json.stringify on client side !
        params = {}
        for key in request.args.keys():
            if key == 'columns' or key == 'order' or key == 'search':
                params[key] = json.loads(request.args[key])
            else:
                params[key] = request.args[key]
        logger.debug("backend request parameters: %s", params)
        # params now contains 'valid' query parameters as Bottle should have found them ...

        parameters = {}
        # Manage page length ...
        parameters['max_results'] = int(params.get('length', 25))

        # Manage page number ...
        parameters['page'] = int(params.get('start', 0))

        # Columns ordering
        # order:[{"column":2,"dir":"desc"}]
        if 'order' in params and params['order']:
            sorted_columns = []
            for order in params['order']:
                idx = int(order['column'])
                logger.info(
                    "sort by column %d (%s), order: %s ",
                    idx, params['columns'][idx]['data'], order['dir']
                )
                if order['dir'] == 'desc':
                    sorted_columns.append('-' + params['columns'][idx]['data'])
                else:
                    sorted_columns.append(params['columns'][idx]['data'])
            if sorted_columns:
                parameters['sort'] = ','.join(sorted_columns)

        # Columns filtering
        # earch:{"value":"test","regex":false}
        if 'search' in params and params['search'] and params['search']['value']:
            logger.info("search all searchable columns containing '%s'", params['search']['value'])
            searched_columns = []
            for column in params['columns']:
                if 'searchable' in column and column['searchable']:
                    searched_columns.append(
                        '{ "%s": { "$regex": ".*%s.*" } }' % (
                            column['data'], params['search']['value']
                        )
                    )
            if searched_columns:
                parameters['where'] = '{"$or": [' + ','.join(searched_columns) + '] }'

        # Request objects from the backend ...
        logger.info("backend parameters: %s", parameters)
        resp = frontend.get_objects(self.object_type, parameters=parameters)
        # page_number = int(resp['_meta']['page'])
        total = int(resp['_meta']['total'])
        # max_results = int(resp['_meta']['max_results'])
        # recordsFiltered = 0
        # if total > max_results:
        # recordsFiltered =

        # Prepare response
        draw = 0
        if request.args.get('draw'):
            draw = int(request.args.get('draw'))
        rsp = {
            "draw": draw,
            "recordsTotal": total,
            "recordsFiltered": total,
            "data": resp['_items']
        }
        # response.content_type = 'application/json'
        logger.info("response: %s", rsp)
        return json.dumps(rsp)

    def table(self):
        """
        Request for elements list

        Returns an HTML page containing filtered elements for an object_type (displays host,
        service, contact, ...) formatted in a jQuery datatable.

        1/ request for data model objects definition
        2/ get main information for objects:
            - list page title,
            - ...
        3/ filter to retain only fields that are managed in the UI

        """
        logger.debug("request for %s list ...", self.object_type)

        # Data model ...
        table_columns = []
        ui_dm = {"title": "All %s (XXX items)" % self.object_type}
        fields = frontend.get_ui_data_model(self.object_type)
        if not fields:
            raise DatatableException(450, "table, trying to get table data for unmanaged data")

        # Objects are considered in the UI
        for field in fields:
            logger.debug("%s field: %s", self.object_type, field)
            if field["name"] == "ui":
                ui_dm["title"] = field["ui"]["title"]
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

        table_columns.sort(key=lambda field: field['name'])

        resp = frontend.get_objects(self.object_type)

        # Update title with number of elements
        if '%d' in ui_dm["title"]:
            ui_dm["title"] = ui_dm["title"] % len(resp['_items'])

        return render_template(
            'list.html',
            object_type=self.object_type,
            title=ui_dm["title"],
            columns=table_columns,
            list=resp['_items']
        )

    def page(self, name='unknown'):
        """
        View page for an element
        """

        return render_template(
            'tpl-%s' % self.object_type,
            app=app,
            element=name
        )
