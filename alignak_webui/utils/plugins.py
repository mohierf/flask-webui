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
    ``alignak_webui.utils.plugins`` module

    Helper functions for plugins
"""

import os
import importlib
import sys
import traceback
import flask
from logging import getLogger
from alignak_webui import app, frontend, manifest, settings

logger = getLogger(__name__)


class Plugins(object):
    """
    Settings parameters
    """

    def __init__(self, application):
        """ .../... """
        self.app = application

    def load_plugins(self, directory=None):
        """
        Load application plugins

        Search for application plugins in the specified directory.

        A plugin is a subdirectory containing a python file named as its directory.

        A plugin file must declare a PLUGIN_NAME variable and a pages dictionary.

        A plugin file must declare a Flask Blueprint object

        :param directory: directory name relative to application working dir
        :type directory: string
        """

        logger.info("loading plugins from directory: %s", directory)
        print "app: %s", directory
        if not os.path.exists(directory):  # pragma: no cover
            logger.error("plugins directory %s does not exist!", directory)
            return 0

        # Get list of sub directories
        plugin_names = [fname for fname in os.listdir(directory)
                        if os.path.isdir(os.path.join(directory, fname))]

        i = 0
        for plugin_name in plugin_names:
            logger.debug("trying to load plugin '%s' ...", plugin_name)
            try:
                sys.path.insert(0, os.path.join(directory, plugin_name))
                plugin = importlib.import_module(plugin_name, __name__)
                try:
                    # Plugins must have a PLUGIN_NAME property to be considered as valid ...
                    logger.debug("loaded plugin file for '%s'", plugin.PLUGIN_NAME)

                    if not hasattr(plugin, plugin_name):
                        continue

                    app.register_blueprint(
                        getattr(plugin, plugin_name),
                        url_prefix='/' + plugin_name
                    )
                    i += 1
                    logger.info("registered plugin '%s'", plugin.PLUGIN_NAME)
                except Exception as e:  # pragma: no cover
                    logger.warning("failed to load plugin '%s', exception: %s",
                                   plugin_name, str(e))
                    logger.warning("Back trace of this kill: %s",
                                   traceback.format_exc())
            except Exception as e:  # pragma: no cover
                logger.warning("failed to load plugin '%s': %s ...", plugin_name, str(e))

        logger.info("loaded %d plugins from: %s", i, directory)
        logger.debug("my routes after plugins loading: %s", app.url_map)

        return i
