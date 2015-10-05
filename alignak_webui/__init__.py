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
    Web User Interface for Alignak REST backend
"""
import re
import flask
from alignak_webui import backend

# Application manifest
VERSION = (0, 1, 0)

__application__ = u"Alignak_Webui"
__version__ = get_version()
__author__ = u"Frédéric MOHIER"
__copyright__ = u"(c) 2015 - %s" % __author__
__license__ = u"GNU Affero General Public License, version 3"
__description__ = u"Web User Interface for Alignak backend"
__releasenotes__ = u"""Bootstrap 3 User Interface for Alignak backend"""
__doc_url__ = u"https://github.com/Alignak-monitoring-contrib/alignak-webui/wiki"
# Application manifest
manifest = {
    'name': __application__,
    'version': __version__,
    'author': __author__,
    'description': __description__,
    'copyright': __copyright__,
    'license': __license__,
    'release': __releasenotes__,
    'doc': __doc_url__,
    'fmw_name': 'Alignak',
    'fmw_version': 'x.y.z'
}

# Main Flask application
app = flask.Flask(__name__.split('.')[0])

# Default configparser settings
settings = {
    'DEBUG': "False",
    'HOST': "127.0.0.1",
    'PORT': "5000"
}

# Frontend connection - create an empty object for it exists
frontend = backend.FrontEnd()


# This import must always remain at the end of this file as recommended in:
# http://flask.pocoo.org/docs/0.10/patterns/packages/
from alignak_webui.user import User
from alignak_webui.utils import assets
from alignak_webui.utils import helper
from alignak_webui import login
from alignak_webui import views
