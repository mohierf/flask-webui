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
Usage:
    {command} [-h] [-d|-v] [-c=cfg_file] [-l=logs_file] [-a=access_log] <command>

Options:
    -h, --help                  Show this screen.
    --version                   Show application version.
    -d, --debug                 Debug mode (DEBUG logs).
    -v, --verbose               Verbose mode (INFO logs).
    -c, --config cfg_file       Specify configuration file [default: settings.cfg]
    -l, --logs logs_file        Specify logs file [default: no application log]
    -a, --access access_log     Specify Web server logs file [default: no access log]

Commands:
    start           Start the application
"""
import os
import sys
from docopt import docopt
from configparser import  ConfigParser
from flask import Flask, session, redirect, url_for, escape, request
import logging
from logging import DEBUG, INFO, WARNING
from logging.handlers import TimedRotatingFileHandler
from datetime import timedelta
from alignak_webui import app, __application__, settings, __version__, __copyright__, __releasenotes__, __license__, __doc_url__

args = docopt(__doc__, help=True, options_first=True, version=__version__)

print args

# Set logging options for the application
if args['--debug']:
    app.logger.setLevel(DEBUG)
    app.debug = True
    app.config['DEBUG'] = True
elif args['--verbose']:
    app.logger.setLevel(INFO)
else:
    app.logger.setLevel(WARNING)

#Set and read configuration file
cfg_file = args['--config']
print 'Required configuration file:', cfg_file
if not os.path.isabs(cfg_file):
    # Searched path
    cfg_etc = os.path.join(os.path.join('/etc', __application__.lower()), cfg_file)
    cfg_home = os.path.expanduser('~/' + __application__.lower() + '.cfg')
    cfg_app = os.path.join(os.path.abspath(os.path.dirname(__file__)), cfg_file)
    # Sub directory ... to be checked after real setup !
    cfg_app = os.path.join(
        os.path.join(os.path.abspath(os.path.dirname(__file__)), __application__.lower()),
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
    print "Required configuration file not found: %s or %s or %s" % (cfg_etc, cfg_home, cfg_app)
    sys.exit(1)

print 'Found configuration file:', cfg_file
config = ConfigParser(defaults=settings)
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
                    app.config[key.upper()] = True if value in ['true', 'True', 'on', 'On', 'y', 'yes', '1'] else False
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
                if settings[section + '.' + option] == -1:
                    print("skip: %s" % section + '.' + option)
            except Exception as e:
                print("exception on %s: %s!", option, str(e))
                settings[section + '.' + option] = None

else:
    app.logger.warning("No configuration file found.")
    print "Required configuration file does not exist: %s" % cfg_file
    sys.exit(1)

# Set logs file
if args['--logs'] != 'no application log':
    # Store logs in a daily file, keeping 6 days along ... as default!
    # Default configuration may be set in configuration file, section [logs]
    fh = TimedRotatingFileHandler(
        filename=args['--logs'],
        when=settings.get('logs.when', 'D'),
        interval=int(settings.get('logs.interval', 1)),
        backupCount=int(settings.get('logs.backupCount', 6))
    )

    fh.setFormatter(logging.Formatter(
        settings.get('logs.formatter', '[%(asctime)s] - %(name)s - %(levelname)s - %(message)s')
    ))
    app.logger.addHandler(fh)
    print "%s logs stored in rotating file: %s" % (__application__, args['--logs'])

if args['--access'] != 'no access log':
    # Store Werkzeug logs  in a daily file, keeping 6 days along ... as default!
    # Default configuration may be set in configuration file, section [logs]
    # Store logs in a daily file, keeping 6 days along ... as default!
    # Default configuration may be set in configuration file, section [logs]
    fh = TimedRotatingFileHandler(
        filename=args['--access'],
        when=settings.get('logs.when', 'D'),
        interval=int(settings.get('logs.interval', 1)),
        backupCount=int(settings.get('logs.backupCount', 6))
    )

    fh.setFormatter(logging.Formatter(
        settings.get('logs.formatter', '[%(asctime)s] - %(name)s - %(levelname)s - %(message)s')
    ))

    logger = logging.getLogger('werkzeug')
    logger.addHandler(fh)
    # Also add the handler to Flask's logger for cases
    #  where Werkzeug isn't used as the underlying WSGI server.
    # app.logger.addHandler(fh)
    # Uncommenting this line makes the application log also available in the access logs file.
    print "server logs stored in rotating file: %s" % args['--access']

try:
    # Application banner in log
    app.logger.info(
        "--------------------------------------------------------------------------------"
    )
    app.logger.info("%s, version %s", __application__, __version__)
    app.logger.info("Copyright %s", __copyright__)
    app.logger.info("License %s", __license__)
    app.logger.info(
        "--------------------------------------------------------------------------------"
    )
    app.logger.info("Doc: %s", __doc_url__)
    app.logger.info("Release notes: %s", __releasenotes__)
    app.logger.info(
        "--------------------------------------------------------------------------------"
    )

    # Application configuration in log
    app.logger.info("Configuration file searched in %s", [cfg_file])
    app.logger.info("Configuration files found: %s", found_cfg_files)
    app.logger.info("Application settings: %s", settings)
    app.logger.info("Flask settings: %s", app.config)

    # self.initialize(debug=args['--debug'], verbose=args['--verbose'])
    if args['<command>'] == 'start':
        app.run(
            host=app.config['HOST'],
            port=app.config['PORT'],
            debug=app.config['DEBUG']
        )
except Exception as e:
    print("failed to launch command '%s', exception: %s / %s", args['<command>'], type(e), str(e))
    app.logger.error("failed to launch command '%s'", args['<command>'])
