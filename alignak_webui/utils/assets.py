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
Web Interface assets
"""
from flask_assets import Bundle, Environment
from alignak_webui import app

bundles = {
    # Login page
    'login_js': Bundle(
        'js/jquery-1.11.3.min.js',
        'js/bootstrap.min.js',
        'js/metisMenu.min.js',
        'js/application.js',
        output='page-login.js',
        filters='jsmin'),

    'login_css': Bundle(
        'css/bootstrap.min.css',
        'css/bootstrap-theme.min.css',
        'css/font-awesome.min.css',
        'css/metisMenu.min.css',
        'css/application.css',
        output='page-login.css',
        filters=['cssrewrite', 'cssmin']),

    # Application page - external assets
    'libs_js': Bundle(
        'js/jquery-1.11.3.min.js',
        'js/bootstrap.min.js',
        'js/metisMenu.min.js',
        'js/jquery.bxslider.min.js',
        'js/alertify.js',
        output='page-libs.js',
        filters='jsmin'),

    'libs_css': Bundle(
        'css/bootstrap.min.css',
        'css/bootstrap-theme.min.css',
        'css/font-awesome.min.css',
        'css/metisMenu.min.css',
        'css/jquery.bxslider.css',
        'css/alertify.css',
        output='page-libs.css',
        filters=['cssrewrite', 'cssmin']),

    # Application page - charts assets
    'charts_js': Bundle(
        'js/Chart.Core.js',
        'js/Chart.Doughnut.js',
        'js/Chart.Bar.js',
        'js/Chart.Line.js',
        'js/Chart.PolarArea.js',
        'js/Chart.Radar.js',
        output='charts-libs.js',
        filters='jsmin'),

    # Application page - own assets
    'app_js': Bundle(
        'js/application.js',
        'js/page-refresh.js',
        output='page-app.js',
        filters='jsmin'),

    'app_css': Bundle(
        'css/application.css',
        output='page-app.css',
        filters=['cssrewrite', 'cssmin'])
}

# Prepare assets
assets = Environment(app)
assets.register(bundles)
