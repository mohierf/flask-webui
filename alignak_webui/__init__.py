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
from flask import Flask

# Application manifest
VERSION = (0, 1, 0)

__application__ = u"Alignak_Webui"
__version__ = '.'.join((str(each) for each in VERSION[:4]))
__copyright__ = u"(c) 2015 - Frédéric MOHIER"
__license__ = u"GNU AGPL version 3"
__releasenotes__ = u"""Bootstrap 3 User Interface for Alignak backend"""
__doc_url__ = u"https://github.com/Alignak-monitoring-contrib/alignak-webui/wiki"

app = Flask(__name__.split('.')[0])

settings = {
    'DEBUG': "False",
    'HOST': "127.0.0.1",
    'PORT': "5000"
}


# setup.py imports this module to gather package version
def get_version():
    """
    Returns shorter version (digit parts only) as string.
    """
    return '.'.join((str(each) for each in VERSION[:4]))

# This import must always remain at the end of this file as recommended in:
# http://flask.pocoo.org/docs/0.10/patterns/packages/
from alignak_webui import views
