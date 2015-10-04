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

import os
from logging import getLogger
from configparser import ConfigParser
from datetime import timedelta
from alignak_webui import app, frontend, manifest, settings

logger = getLogger(__name__)


class Settings(object):
    """
    Settings parameters
    """

    def __init__(self, application):
        """ .../... """
        self.app = application

    def read(self, cfg_file, default):
        """ Read configuration file """
        if not os.path.isabs(cfg_file):
            # Searched path
            cfg_etc = os.path.join(os.path.join('/etc', manifest['name'].lower()), cfg_file)
            cfg_home = os.path.expanduser('~/' + manifest['name'].lower() + '.cfg')
            cfg_app = os.path.join(os.path.abspath(os.path.dirname(__file__)), cfg_file)
            # Sub directory ... to be checked after real setup !
            cfg_app = os.path.join(
                os.path.join(os.path.dirname(__file__), os.path.pardir),
                cfg_file
            )

            # In /etc/alignak_webui ...
            if os.path.isfile(cfg_etc):
                cfg_file = cfg_etc
            # In current directory ...
            elif os.path.isfile(cfg_app):
                cfg_file = cfg_app
            # In user home directory ...
            elif os.path.isfile(cfg_home):
                cfg_file = cfg_home

        if not os.path.isfile(cfg_file):
            print "Required configuration file not found: %s or %s or %s" % (
                cfg_etc, cfg_home, cfg_app
            )
            return None

        cfg_file = os.path.abspath(cfg_file)

        config = ConfigParser(defaults=default)
        found_cfg_files = config.read([cfg_file])
        if found_cfg_files:
            # Build Flask configuration parameters
            if config.has_section('flask'):
                for key, value in config.items('flask'):
                    if key.upper() in app.config:
                        app_default = app.config[key.upper()]
                        if isinstance(app_default, timedelta):
                            app.config[key.upper()] = timedelta(value)
                        elif isinstance(app_default, bool):
                            app.config[key.upper()] = True if value in [
                                'true', 'True', 'on', 'On', 'y', 'yes', '1'
                            ] else False
                        elif isinstance(app_default, float):
                            app.config[key.upper()] = float(value)
                        elif isinstance(app_default, int):
                            app.config[key.upper()] = int(value)
                        else:
                            # All the string keys need to be coerced into str()
                            # because Flask expects some of them not to be unicode
                            app.config[key.upper()] = str(value)
                    else:
                        if value.isdigit():
                            app.config[key.upper()] = int(value)
                        else:
                            app.config[key.upper()] = str(value)
            else:
                app.config['HOST'] = '127.0.0.1'
                app.config['PORT'] = 80
                app.config['DEBUG'] = False

            # Build a secret key if none defined ...
            if 'SECRET_KEY' not in app.config or not app.config['SECRET_KEY']:
                app.config['SECRET_KEY'] = os.urandom(24)

            # Build settings dictionnary for application parameters
            for section in config.sections():
                for option in config.options(section):
                    try:
                        settings[section + '.' + option] = config.get(section, option)
                        app.config[section + '.' + option] = config.get(section, option)
                        if settings[section + '.' + option] == -1:
                            print "skip: %s" % section + '.' + option
                    except Exception:
                        settings[section + '.' + option] = None
                        app.config[section + '.' + option] = None

        else:
            app.logger.warning("No configuration file found.")
            print "Required configuration file does not exist: %s" % cfg_file
            return None

        return cfg_file
