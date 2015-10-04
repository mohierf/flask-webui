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

import json
from logging import getLogger
from alignak_webui import app, frontend

logger = getLogger(__name__)


class Helper(object):
    """
    Helper class

    Functions used in HTML templates to help building some elements
    """
    host_states = [
        'UP', 'DOWN', 'UNREACHABLE', 'PENDING', 'UNKNOWN'
    ]
    extra_host_states = [
        'FLAPPING', 'ACK', 'DOWNTIME'
    ]
    service_states = [
        'OK', 'CRITICAL', 'WARNING', 'PENDING', 'UNKNOWN'
    ]
    extra_service_states = [
        'FLAPPING', 'ACK', 'DOWNTIME'
    ]

    def __init__(self, application):
        """To be checked"""
        self.app = application

    @staticmethod
    def print_date(t, fmt='%Y-%m-%d %H:%M:%S'):
        """
        For a unix timestamp return something like
        2015-09-18 00:00:00

        Returns n/a if provided timestamp is not valid

        :param t: unix timestamp
        :type t: long int
        :param fmt: python date/time format string
        :type fmt: sting
        :return: formatted date
        :rtype: string
        """
        if not t:
            return 'n/a'

        return time.strftime(fmt, time.localtime(t))

    @staticmethod
    def print_duration(t, duration_only=False, x_elts=0):
        """
        For a unix timestamp return something like
        1h 15m 12s

        Returns n/a if provided timestamp is not valid

        Returns:
        in 1h 15m 12s
        Now
        1h 15m 12s ago

        Returns 1h 15m 12s if only_duration is True

        :param t: unix timestamp
        :type t: long int
        :param fmt: python date/time format string
        :type fmt: sting
        :return: formatted date
        :rtype: string
        """
        if not t:
            return 'n/a'

        # Get the difference between now and the time of the user
        seconds = int(time.time()) - int(t)

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

    def get_business_impact_text(self, business_impact, icon=True, text=True):
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

    def get_state_text(self, obj_type, state, extra='',
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
        :param extra: DOWNTIME, ACK or FLAPPING
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

        if (obj_type == 'host' and state.upper() not in Helper.host_states) or (
                obj_type == 'host' and extra and extra.upper() not in Helper.extra_host_states):
            return 'n/a'

        if (obj_type == 'service' and state.upper() not in Helper.service_states) or (
                obj_type == 'service' and
                extra and extra.upper() not in Helper.extra_service_states):
            return 'n/a'

        if not icon and not text:
            return 'n/a'

        # Text
        res_icon_text = app.config.get(
            "ui.%s_text_%s" % (obj_type, state.lower()),
            'unknown'
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
        if extra and extra in ['ACK', 'DOWNTIME']:
            res_style = 'style="opacity: 0.5" '

        # Assembling ...
        res_icon = res_icon_global
        res_icon = res_icon.replace("##back##", res_icon_back)
        res_icon = res_icon.replace("##front##", res_icon_front)
        res_icon = res_icon.replace("##state##", state)
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

    def get_url(self, obj_type, name, label=None, title=None):
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

# Prepare helper object
helper = Helper(app)
