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
    ``alignak_webui.utils.helper`` module

    Helper functions used in templates
"""

import time
import copy
import math
import operator
import re
import itertools

import json
from logging import getLogger
from alignak_webui import app, frontend
from flask_login import current_user

logger = getLogger(__name__)


class Helper(object):
    """
    Helper class

    Functions used in HTML templates to help building some elements
    """
    host_states = [
        'UP', 'DOWN', 'UNREACHABLE'
    ]
    extra_host_states = [
        'FLAPPING', 'ACKNOWLEDGED', 'IN_DOWNTIME'
    ]
    service_states = [
        'OK', 'CRITICAL', 'WARNING', 'UNKNOWN'
    ]
    extra_service_states = [
        'FLAPPING', 'ACKNOWLEDGED', 'IN_DOWNTIME'
    ]

    search_name = None
    search_string = None
    livestate = None
    livestate_age = None

    def __init__(self, application):
        """Store application reference"""
        self.app = application

    @staticmethod
    def print_date(timestamp, fmt='%Y-%m-%d %H:%M:%S'):
        """
        For a unix timestamp return something like
        2015-09-18 00:00:00

        Returns n/a if provided timestamp is not valid

        :param timestamp: unix timestamp
        :type timestamp: long int
        :param fmt: python date/time format string
        :type fmt: sting
        :return: formatted date
        :rtype: string
        """
        if not timestamp:
            return 'n/a'

        return time.strftime(fmt, time.localtime(timestamp))

    @staticmethod
    def print_duration(timestamp, duration_only=False, x_elts=0):
        """
        For a unix timestamp return something like
        1h 15m 12s

        Returns n/a if provided timestamp is not valid

        Returns:
        in 1h 15m 12s
        Now
        1h 15m 12s ago

        Returns 1h 15m 12s if only_duration is True

        :param timestamp: unix timestamp
        :type timestamp: long int
        :param fmt: python date/time format string
        :type fmt: sting
        :return: formatted date
        :rtype: string
        """
        if not timestamp:
            return 'n/a'

        # Get the difference between now and the time of the user
        seconds = int(time.time()) - int(timestamp)

        # If it's now, say it :)
        if seconds == 0:
            return 'Now'

        in_future = False

        # Remember if it's in the future or not
        if seconds < 0:
            in_future = True

        # Now manage all case like in the past
        seconds = abs(seconds)

        seconds = long(round(seconds))
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        weeks, days = divmod(days, 7)
        months, weeks = divmod(weeks, 4)
        years, months = divmod(months, 12)

        minutes = long(minutes)
        hours = long(hours)
        days = long(days)
        weeks = long(weeks)
        months = long(months)
        years = long(years)

        duration = []
        if years > 0:
            duration.append('%dy' % years)
        else:
            if months > 0:
                duration.append('%dM' % months)
            if weeks > 0:
                duration.append('%dw' % weeks)
            if days > 0:
                duration.append('%dd' % days)
            if hours > 0:
                duration.append('%dh' % hours)
            if minutes > 0:
                duration.append('%dm' % minutes)
            if seconds > 0:
                duration.append('%ds' % seconds)

        # Now filter the number of printed elements if ask
        if x_elts >= 1:
            duration = duration[:x_elts]

        # Maybe the user just want the duration
        if duration_only:
            return ' '.join(duration)

        # Now manage the future or not print
        if in_future:
            return 'in ' + ' '.join(duration)
        else:
            return ' '.join(duration) + ' ago'

    def get_html_business_impact(self, business_impact, icon=True, text=True):
        """
        Returns a business impact as HTML text and icon if needed

        If parameters are not valid, returns 'n/a'

        Text and icon are defined in the application configuration file.

        :param business_impact: value of business impact (0 to 5)
        :type business_impact: int
        :param text: include text in the response
        :type text: boolean
        :param icon: include icon in the response
        :type icon: boolean
        :return: formatted BI HTML string
        :rtype: string
        """
        if not 0 <= business_impact <= 5:
            return 'n/a'

        if not icon and not text:
            return 'n/a'

        # Icon
        res_icon = app.config.get(
            "ui.bi_icon", '<i class="fa fa-star text-primary"></i>'
        ) * max(0, business_impact - 2)

        # Text
        res_text = app.config.get("ui.bi_%d" % business_impact, 'unknown')

        result = ""
        if text and icon:
            if res_icon:
                result = "%s %s" % (res_text, res_icon)
            else:
                result = res_text
        elif text and not icon:
            result = res_text
        else:
            result = res_icon

        return result

    def get_html_state(self, obj_type, state, extra='',
                       icon=True, text=False, label='', disabled=False):
        """
        Returns an host/Service state as HTML text and icon if needed

        If parameters are not valid, returns 'n/a'

        obj_type and state specify which object type is in which state

        extra specifies an extra state information (ACK, DOWNTIME or FLAPPING)

        If disabled is True, the used font is greyed

        If a label is specified, text must be True, and the label will be used instead
        of the built text.

        Text and icon are defined in the application configuration file.

        Template based synatx:
        To be described ...
        # ##sytle##
        # ##title##
        # ##back##
        # ##front##
        # ##text##
        # ##state##
        # ##font##

        Host state text (example with default configuration):
            <span class="fa-stack" title="host state is DOWN and flapping">
                <i class="fa fa-circle fa-stack-2x font-down"></i>
                <i class="fa fa-server fa-stack-1x font-down"></i>
                host state is DOWN and flapping
            </span>

            <span class="font-up">
                <span class="fa-stack" title="host state is UP">
                    <i class="fa fa-circle fa-stack-2x font-up"></i>
                    <i class="fa fa-server fa-stack-1x fa-inverse"></i>
                <span>
                8 <i>(66.67%)</i></span></span></span>

            <span class="font-up">
                <span class="fa-stack" title="host is UP">
                    <i class="fa fa-circle fa-stack-2x font-up"></i>
                    <i class="fa fa-server fa-stack-1x fa-inverse"></i>
                </span>
                <span class="num">1 <i>(25.0%)</i></span>
            </span>

        :param obj_type: host or service
        :type obj_type: string
        :param state: host state or service state
        :type state: string
        :param extra: IN_DOWNTIME, ACKNOWLEDGED or FLAPPING
        :type extra: string
        :param text: include text in the response
        :type text: boolean
        :param icon: include icon in the response
        :type icon: boolean
        :return: formatted state HTML string
        :rtype: string
        """
        if obj_type not in ['host', 'service']:
            return 'n/a'

        if (obj_type == 'host' and state and state.upper() not in Helper.host_states) or (
                obj_type == 'host' and extra and extra.upper() not in Helper.extra_host_states):
            return 'n/a'

        if (obj_type == 'service' and state and state.upper() not in Helper.service_states) or (
                obj_type == 'service' and
                extra and extra.upper() not in Helper.extra_service_states):
            return 'n/a'

        if not icon and not text:
            return 'n/a'

        # Text
        res_icon_text = app.config.get(
            "ui.%s_text_%s" % (obj_type, state.lower()),
            'State is insignificant'
        )
        res_text = res_icon_text

        if extra:
            res_extra = app.config.get(
                "ui.%s_text_%s" % (obj_type, extra.lower()),
                ''
            )
            res_text = "%s %s" % (res_text, res_extra)

        if text and not icon:
            return res_text

        # Icon
        res_icon_global = app.config.get(
            "ui.host_state_content",
            '<span class="fa-stack" ##style## title="##title##">##back####front##</span>'
        )
        res_icon_back = app.config.get(
            "ui.host_state_back",
            '<i class="fa fa-circle fa-stack-2x font-##state##"></i>'
        )
        res_icon_front = app.config.get(
            "ui.host_state_front",
            '<i class="fa fa-##state## fa-stack-1x ##extra##"></i>'
        )
        res_icon_state = app.config.get(
            "ui.%s_icon_%s" % (obj_type, state.lower()),
            'question'
        )
        res_extra = "fa-inverse"
        if extra and extra == 'FLAPPING':
            res_extra = "font-%s" % state.lower()
        res_style = ""
        if extra and extra in ['ACKNOWLEDGED', 'IN_DOWNTIME']:
            res_style = 'style="opacity: 0.5" '

        # Assembling ...
        res_icon = res_icon_global
        res_icon = res_icon.replace("##back##", res_icon_back)
        res_icon = res_icon.replace("##front##", res_icon_front)
        res_icon = res_icon.replace("##state##", state.lower())
        if not disabled:
            res_icon = res_icon.replace("##font##", "font-" + state.lower())
        else:
            res_icon = res_icon.replace("##font##", "font-greyed")
        res_icon = res_icon.replace("##icon##", res_icon_state)
        res_icon = res_icon.replace("##extra##", res_extra)
        res_icon = res_icon.replace("##title##", res_text)
        res_icon = res_icon.replace("##style##", res_style)
        if label:
            res_icon = res_icon.replace("##text##", label)
        elif text:
            res_icon = res_icon.replace("##text##", res_text)
        else:
            res_icon = res_icon.replace("##text##", "")

        return res_icon

    def get_html_id(self, obj_type, name):
        """
        Returns an host/service/contact ... HTML identifier

        If parameters are not valid, returns 'n/a'

        obj_type specifies object type
        name specifes the object name

        :param obj_type: host, service, contact
        :type obj_type: string
        :param name: object name
        :type name: string

        :return: valid HTML identifier
        :rtype: string
        """
        if not obj_type or not name:
            return 'n/a'

        return re.sub('[^A-Za-z0-9-_]', '', "%s-%s" % (obj_type, name))

    def get_html_url(self, obj_type, name, label=None, title=None):
        """
        Returns an host/service/contact ... url

        If parameters are not valid, returns 'n/a'

        obj_type specifies object type

        name specifes the object name

        :param obj_type: host, service, contact
        :type obj_type: string
        :param name: object name
        :type state: string
        :param label: label for the link
        :type label: string

        :return: link to the object url
        :rtype: string
        """
        if not obj_type or not name:
            return 'n/a'

        return """<a href="/%s/%s" title="%s">%s</a>""" % (
            obj_type, name,
            title if title else name,
            label if label else name
        )

    def get_livestate(self, parameters=None):
        """
        Get live state from backend

        Live state is a list of items with those fields:
        {
            u'host_name': u'56080340f9e3858df8c5f5d5',
            u'service_description': u'56080343f9e3858df8c5f67f',
            u'acknowledged': False,
            u'last_check': 1443375659,
            u'state_type': u'HARD',
            u'state': u'OK',
            u'output': u'...',
            u'long_output': u'...',
            u'perf_data': u'...'
            u'_created': u'Sun, 27 Sep 2015 15:14:04 GMT',
            u'_updated': u'Sun, 27 Sep 2015 17:41:02 GMT',
            u'_id': u'560807bcf9e38523556deffe',
            u'_etag': u'c9ce5d09248a41c1061bd1b416c5f2dba247d50d',
            u'_links': {
                u'self': {
                    u'href': u'livestate/560807bcf9e38523556deffe', u'title': u'Livestate'
                }
            },
        }

        host_name and service_description fields are embedded. Those fields are dictionaries of
        fields describing an host and a service.

        :param parameters: search parameters for the backend
        :type parameters: dict

        :return: list of livestate elements
        :rtype: list
        """
        if Helper.livestate_age and (int(time.time()) - Helper.livestate_age) <= 60:
            logger.debug(
                "get_livestate, return self stored livestate, %d elements",
                len(Helper.livestate)
            )
            return Helper.livestate

        if not parameters:
            parameters = {}

        if "embedded" not in parameters:
            parameters.update({"embedded": '{"host_name": 1, "service_description": 1}'})
        if "sort" not in parameters:
            parameters.update({"sort": 'host_name, service_description'})
        # if "where" not in parameters:
            # parameters.update({"where": '{"state":true}'})

        Helper.livestate = frontend.get_livestate(parameters=parameters)
        hosts_ids = {}
        # Searching for hosts first ...
        for item in Helper.livestate:
            if not item['service_description']:
                item['type'] = 'host'
                item['id'] = item['host_name']['host_name']
                item['bi'] = int(item['host_name']['business_impact'])
                item['name'] = item['host_name']['host_name']
                item['last_state_change'] = item['last_check']
                item['friendly_name'] = ""
                if 'alias' in item['host_name']:
                    if item['host_name']['alias']:
                        item['friendly_name'] = item['host_name']['alias']
                if 'display_name' in item['host_name']:
                    if item['host_name']['display_name']:
                        item['friendly_name'] = item['host_name']['display_name']

                # Build an hosts cache ...
                if not item['host_name']['_id'] in hosts_ids:
                    hosts_ids[item['host_name']['_id']] = item['host_name']['host_name']

        # Searching for services next ...
        for item in Helper.livestate:
            if item['service_description']:
                item['type'] = 'service'
                item['id'] = item['service_description']['service_description']
                item['bi'] = int(item['service_description']['business_impact'])
                item['name'] = "%s/%s" % (
                    hosts_ids[item['service_description']['host_name']],
                    item['service_description']['service_description']
                )
                item['last_state_change'] = item['last_check']
                item['friendly_name'] = ""
                if 'alias' in item['service_description']:
                    if item['service_description']['alias']:
                        item['friendly_name'] = item['service_description']['alias']
                if 'display_name' in item['service_description']:
                    if item['service_description']['display_name']:
                        item['friendly_name'] = item['service_description']['display_name']

        Helper.livestate_age = int(time.time())
        return Helper.livestate

    def get_html_livestate(self, bi=0, filter=None):
        """
        Get HTML formatted live state

        Update system live synthesis and build header elements

        :param bi: business impact
        :type bi: int

        :return: hosts_states and services_states HTML strings in a dictionary
        :rtype: dict
        """
        parameters = {}
        if bi:
            parameters.update({"where": '{"bi":%d}' % bi})

        items = self.get_livestate(parameters=parameters)
        if bi:
            items = [item for item in items if item['bi'] == bi]

        rows = []
        current_host = ''
        for item in items:
            id = self.get_html_id(item['type'], item['name'])

            host_url = ''
            if current_host != item['host_name']['host_name']:
                current_host = item['host_name']['host_name']
                host_url = self.get_html_url("host", item['host_name']['host_name'])

            service_url = 'Host check'
            if item['type'] == "service":
                service_url = self.get_html_url(
                    "service", item['service_description']['service_description']
                )

            long_output = ''
            if item['long_output']:
                long_output = """
                    <button
                        type="button"
                        class="btn btn-xs btn-info"
                        data-toggle="popover"
                        title="Long output"
                        data-content="Long check output ...">
                        %s
                        </button>
                """ % item['long_output']

            tr = """
            <tr data-toggle="collapse" data-target="#details-%s" class="accordion-toggle">
                <td>
                    <input
                        id="selector-%s"
                        type="checkbox" class="input-sm" value=""
                        data-type="problem" data-business-impact="0" data-item="xxxx">
                </td>
                <td>
                    %s
                </td>
                <td>
                    %s
                </td>
                <td>
                    %s
                </td>
                <td class="font-%s"><strong>%s</strong></td>
                <td class="hidden-sm hidden-xs">
                    %s
                </td>
                <td class="hidden-sm hidden-xs">
                    %s
                    %s
                </td>
            </tr>""" % (
                id,
                id,
                self.get_html_state(item["type"], item["state"]),
                host_url,
                service_url,
                item['state'].lower(),
                item['state'],
                self.print_duration(item['last_state_change'], duration_only=True, x_elts=2),
                item['output'],
                long_output
            )
            rows.append(tr)

            if item['type'] == "host":
                passive_checks_enabled = item['host_name']['passive_checks_enabled']
                freshness_threshold = item['host_name']['freshness_threshold']
                active_checks_enabled = item['host_name']['active_checks_enabled']
            else:
                passive_checks_enabled = item['service_description']['passive_checks_enabled']
                freshness_threshold = item['service_description']['freshness_threshold']
                active_checks_enabled = item['service_description']['passive_checks_enabled']
            tr2 = """
            <tr>
                <td colspan="20" class="hiddenRow">
                    <div class="accordion-body collapse" id="details-%s">""" % (id)
            if passive_checks_enabled:
                tr2 += """
                    <td>
                        <i class="fa fa-arrow-left" title="Passive checks are enabled."></i>"""
            if freshness_threshold:
                tr2 += """
                        <i title="Freshness check is enabled">(Freshness threshold: %s seconds)</i>
                    </td>""" % (freshness_threshold)
            if active_checks_enabled:
                tr2 += """
                <td>
                    <i class="fa fa-arrow-right" title="Active checks are enabled."></i>
                    <i>
                        Last check <strong>%s</strong>,
                        next check in <strong>???</strong>,
                        attempt <strong>???</strong>
                    </i>
                </td>""" % (helper.print_duration(item['last_check'], duration_only=True, x_elts=2))

            if current_user and current_user.can_action():
                tr2 += """
                    <td align="right">
                        <div class="btn-group"
                            role="group" data-type="actions" aria-label="Actions">
                            <button class="btn btn-default btn-xs"
                            data-type="action" action="event-handler"
                            data-toggle="tooltip" data-placement="bottom"
                            title="Try to fix (launch event handler)"
                            data-element="test">
                            <i class="fa fa-magic"></i>
                            <span class="hidden-sm hidden-xs"> Try to fix</span>
                            </button>
                        </div>
                    </td>"""

            tr2 += """
                    </div>
                </td>
            </tr>"""

            rows.append(tr2)

        panel_bi = """
            <div id="livestate-bi-%d" class="panel panel-default">
                <div class="panel-body">
                    <button type="button" class="btn btn-default btn-xs pull-left"
                        data-type="business-impact" data-business-impact="%d" data-state="off">
                        Select all elements
                    </button>

                    <i class="pull-right small">%d elements</i>
                    <h3 class="text-center">Business impact: %s</h3>

                    <table class="table table-invisible table-condensed">
                        <thead><tr>
                            <th width="20px"></th>
                            <th width="40px"></th>
                            <th width="60px">Host</th>
                            <th width="90px">Service</th>
                            <th width="90px">State</th>
                            <th class="hidden-sm hidden-xs" width="90px">Duration</th>
                            <th class="hidden-sm hidden-xs" width="100%%">Output</th>
                        </tr></thead>

                        <tbody>
                        </tbody>
                    </table>
                </div>
            </div>""" % (bi, bi, len(rows), self.get_html_business_impact(bi, icon=True, text=True))

        return {'bi': bi, 'rows': rows, 'panel_bi': panel_bi}

    def get_livesynthesis(self):
        """Get live synthesis from backend"""
        return frontend.get_livesynthesis()

    def get_html_livesynthesis(self):
        """
        Get HTML formatted live sythesis

        Update system live synthesis and build header elements

        :return: hosts_states and services_states HTML strings in a dictionary
        :rtype: dict
        """
        ls = self.get_livesynthesis()

        if not ls:
            return {
                'hosts_states_popover': "",
                'services_states_popover': "",
                'hosts_state': """
                    <a tabindex="0" role="button" title="Overall hosts states unknown">
                        <i class="fa fa-server"></i>
                        <span class="label label-as-badge label-unknown">?</span>
                    </a>
                """,
                'services_state': """
                    <a tabindex="0" role="button" title="Overall services states unknown">
                        <i class="fa fa-bars"></i>
                        <span class="label label-as-badge label-unknown">?</span>
                    </a>
                """
            }

        hosts_states_popover = ''
        lsh = ls['hosts_synthesis']
        for state in Helper.host_states:
            try:
                nb = int(lsh["nb_%s" % state.lower()])
                pct = float(lsh["pct_%s" % state.lower()])
                label = "<small>%d (%s %%)</small>" % (nb, pct)
                hosts_states_popover += '<td data-state="%s" data-count="%d">%s</td>' % (
                    state.lower(),
                    nb,
                    helper.get_html_state(
                        "host", state.lower(), label=label, disabled=False
                    )
                )
            except KeyError:
                continue

        for state in Helper.extra_host_states:
            try:
                nb = int(lsh["nb_%s" % state.lower()])
                pct = float(lsh["pct_%s" % state.lower()])
                label = "<small>%d (%s %%)</small>" % (nb, pct)
                hosts_states_popover += '<td data-state="%s" data-count="%d">%s</td>' % (
                    state.lower(),
                    nb,
                    helper.get_html_state(
                        "host", "", extra=state, label=label, disabled=False
                    )
                )
            except KeyError:
                continue

        hosts_states_popover = """<table class="table table-invisible table-condensed"><tbody>
        <tr data-count="%d" data-problems="%d">%s</tr>
        </tbody></table>""" % (
            int(lsh["nb_elts"]),
            int(lsh["nb_problems"]),
            hosts_states_popover
        )

        overall_state = "up"
        if float(lsh["pct_problems"]) >= 100.0 - float(app.config.get("ui.hosts_warning", 5)):
            overall_state = "unreachable"
        if float(lsh["pct_problems"]) >= 100.0 - float(app.config.get("ui.hosts_critical", 5)):
            overall_state = "down"

        hosts_state = """
        <a tabindex="0" role="button" title="Overall hosts states, %d hosts, %d problems">
            <i class="fa fa-server"></i>
            <span class="label label-as-badge label-%s">%d</span>
        </a>
        """ % (
            int(lsh["nb_elts"]),
            int(lsh["nb_problems"]),
            overall_state,
            int(lsh["nb_problems"])
        )

        services_states_popover = ''
        lss = ls['services_synthesis']
        for state in Helper.service_states:
            try:
                nb = int(lss["nb_%s" % state.lower()])
                pct = float(lss["pct_%s" % state.lower()])
                label = "<small>%s (%s %%)</small>" % (nb, pct)
                services_states_popover += '<td data-state="%s" data-count="%d">%s</td>' % (
                    state.lower(),
                    nb,
                    helper.get_html_state(
                        "service", state.lower(), label=label, disabled=False
                    )
                )
            except KeyError:
                continue

        for state in Helper.extra_service_states:
            try:
                nb = int(lss["nb_%s" % state.lower()])
                pct = float(lss["pct_%s" % state.lower()])
                label = "<small>%s (%s %%)</small>" % (nb, pct)
                services_states_popover += '<td data-state="%s" data-count="%d">%s</td>' % (
                    state.lower(),
                    nb,
                    helper.get_html_state(
                        "service", "", state, label=label, disabled=False
                    )
                )
            except KeyError:
                continue

        services_states_popover = """
        <table class="table table-invisible table-condensed"><tbody>
        <tr data-count="%d" data-problems="%d">%s</tr>
        </tbody></table>
        """ % (
            int(lss["nb_elts"]), int(lss["nb_problems"]), services_states_popover
        )

        overall_state = "ok"
        if float(lss["pct_problems"]) >= 100.0 - float(app.config.get("ui.services_warning", 5)):
            overall_state = "warning"
        if float(lss["pct_problems"]) >= 100.0 - float(app.config.get("ui.services_critical", 5)):
            overall_state = "critical"

        services_state = """
        <a tabindex="0" role="button" title="Overall services states, %d services, %d problems">
            <i class="fa fa-bars"></i>
            <span class="label label-as-badge label-%s">%d</span>
        </a>
        """ % (
            int(lss["nb_elts"]),
            int(lss["nb_problems"]),
            overall_state,
            int(lss["nb_problems"])
        )

        return {
            'hosts_states_popover': hosts_states_popover,
            'services_states_popover': services_states_popover,
            'hosts_state': hosts_state,
            'services_state': services_state
        }

    def search_livestate(self, search, sorter=None):
        """
        Search in items list.

        :param search: Search string
        :type search: str
        :param items: list of items to search in, if None, the function gets the system livestate
        :type items: list
        :param sorter: function to sort the items. default=None (means no sorting)
        :type sorter: function
        :return: list of hosts and services
        :rtype: list
        """
        logger.debug("searching, pattern: %s", search)

        items = self.livestate
        if not items:
            logger.warning("searching, livestate is empty")
            return []
        logger.debug("searching, livestate: %d items", len(items))

        search_patterns = [s for s in search.split(' ')]

        for pattern in search_patterns:
            pattern = pattern.strip()
            if not pattern:
                continue

            search_type = 'search_name'
            parameter = pattern
            elts = pattern.split(':', 1)
            if len(elts) > 1:
                search_type = elts[0]
                parameter = elts[1].lower()

            search_type = search_type.lower()
            logger.debug("searching, search type: '%s', parameter: '%s'", search_type, parameter)

            if search_type == 'search_name':
                pat_regex = re.compile(parameter, re.IGNORECASE)
                new_items = []
                # Search pattern in elements name ...
                for item in items:
                    if pat_regex.search(item['name']):
                        new_items.append(item)
                logger.debug(
                    "searching, name contains: %s, found %d elements",
                    parameter, len(new_items)
                )

                # ... else search pattern in livestate output
                if not new_items:
                    for item in items:
                        if (pat_regex.search(item['output']) or
                                pat_regex.search(item['long_output'])):
                            new_items.append(item)
                    logger.debug(
                        "searching, output contains: %s, found %d elements",
                        parameter, len(new_items)
                    )

                # ... should search pattern in some other fields ?

                items = new_items

            if search_type == 'type':
                if parameter == 'host':
                    items = [item for item in items if item['type'] == 'host']
                elif parameter == 'service':
                    items = [item for item in items if item['type'] == 'service']
                elif parameter != 'all':
                    logger.warning("searching type parameter is not recognized: %s", parameter)
                    continue
                logger.debug(
                    "searching, element type: %s, found %d elements",
                    parameter, len(items)
                )

            if search_type == 'bp' or search_type == 'bi':
                logger.debug("searching, business impact: %s", parameter)
                if parameter.startswith('>='):
                    items = [item for item in items if item['bi'] >= int(parameter[2:])]
                elif parameter.startswith('<='):
                    items = [item for item in items if item['bi'] <= int(parameter[2:])]
                elif parameter.startswith('>'):
                    items = [item for item in items if item['bi'] > int(parameter[1:])]
                elif parameter.startswith('<'):
                    items = [item for item in items if item['bi'] < int(parameter[1:])]
                elif parameter.startswith('='):
                    parameter = parameter[1:]
                elif parameter.isdigit():
                    items = [item for item in items if item['bi'] == int(parameter)]
                logger.debug(
                    "searching, business impact: %s, found %d elements",
                    parameter, len(items)
                )

            if search_type == 'is':
                if parameter.lower() == 'ack':
                    items = [item for item in items if item['acknowledged']]
                elif parameter.lower() == 'downtime':
                    items = [item for item in items if item['in_scheduled_downtime']]
                elif parameter.lower() == 'impact':
                    items = [item for item in items if item['is_impact']]
                else:
                    if parameter.isdigit():
                        items = [
                            item for item in items if
                            item['state'] == Helper.host_states[int(parameter)]
                        ]
                    else:
                        items = [
                            item for item in items if item['state'] == parameter.upper()
                        ]
                logger.debug(
                    "searching, %s:%s, found %d elements",
                    search_type, parameter, len(items)
                )

            if search_type == 'isnot':
                if parameter.lower() == 'ack':
                    items = [item for item in items if not item['acknowledged']]
                elif parameter.lower() == 'downtime':
                    items = [item for item in items if not item['in_scheduled_downtime']]
                elif parameter.lower() == 'impact':
                    items = [item for item in items if not item['is_impact']]
                else:
                    if parameter.isdigit():
                        items = [
                            item for item in items if
                            item['state'] != Helper.host_states[int(parameter)]
                        ]
                    else:
                        items = [
                            item for item in items if item['state'] != parameter.upper()
                        ]
                logger.debug(
                    "searching, %s:%s, found %d elements",
                    search_type, parameter, len(items)
                )

            # Search shortcuts
            if search_type == 'host':
                search_patterns.append("type:host")
            if search_type == 'service':
                search_patterns.append("type:service")
            if search_type == 'ack':
                if parameter == 'false' or parameter == 'no' or parameter == '0':
                    search_patterns.append("isnot:ack")
                if parameter == 'true' or parameter == 'yes' or parameter == '1':
                    search_patterns.append("is:ack")
            if search_type == 'downtime':
                if parameter == 'false' or parameter == 'no' or parameter == '0':
                    search_patterns.append("isnot:downtime")
                if parameter == 'true' or parameter == 'yes' or parameter == '1':
                    search_patterns.append("is:downtime")
            if search_type in Helper.host_states or search_type in Helper.extra_host_states:
                search_patterns.append("is:%s" % search_type)
            if search_type in Helper.service_states or search_type in Helper.extra_service_states:
                search_patterns.append("is:%s" % search_type)

        if sorter is not None:
            items.sort(sorter)

        return items

# Prepare helper object
helper = Helper(app)
