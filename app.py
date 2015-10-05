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
import logging
import traceback
from logging.handlers import TimedRotatingFileHandler
from alignak_webui import app, frontend, manifest, settings
from alignak_webui import __name__ as __pkg_name__

from alignak_webui.backend import FrontEnd
from alignak_webui.user import User
from alignak_webui.utils.settings import Settings
from alignak_webui.utils.plugins import Plugins


def main():
    args = docopt(__doc__, help=True, options_first=True, version=manifest['version'])

    # Set application logger name
    app.logger_name = __pkg_name__

    # Set logging options for the application
    logger = logging.getLogger(app.logger_name)
    logger.setLevel(logging.WARNING)

    # Create a console handler, add a formatter and set level to DEBUG
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    # Add console handler to logger
    app.logger.addHandler(ch)

    if args['--debug']:
        app.logger.setLevel(logging.DEBUG)
        app.debug = True
        app.config['DEBUG'] = True
    elif args['--verbose']:
        app.logger.setLevel(logging.INFO)

    # Set and read configuration file
    cfg_file = args['--config']
    print 'Required configuration file:', cfg_file
    sett = Settings(app)
    found_cfg_files = sett.read(cfg_file, settings)
    if not found_cfg_files:
        print "Required configuration file not found."
        sys.exit(1)
    print 'Found configuration file:', cfg_file

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
        print "%s logs stored in rotating file: %s" % (manifest['name'].lower(), args['--logs'])

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
        # Update application manifest
        manifest['fmw_name'] = settings['framework.name']
        manifest['fmw_version'] = settings['framework.version']
        manifest['webui_logo'] = settings.get(
            'ui.webui_logo', '/static/images/logo_webui.png'
        )
        manifest['footer_logo'] = settings.get(
            'ui.footer_logo', '/static/images/logo_webui_xxs.png'
        )
        manifest['company_logo'] = settings.get(
            'ui.company_logo', '/static/images/default_company.png'
        )
        manifest['login_text'] = settings['ui.welcome_text']

        # Application banner in log
        app.logger.info(
            "--------------------------------------------------------------------------------"
        )
        app.logger.info("%s, version %s", manifest['name'], manifest['version'])
        app.logger.info("Copyright %s", manifest['copyright'])
        app.logger.info("License %s", manifest['license'])
        app.logger.info(
            "--------------------------------------------------------------------------------"
        )
        app.logger.debug("Doc: %s", manifest['doc'])
        app.logger.debug("Release notes: %s", manifest['release'])
        app.logger.debug(
            "--------------------------------------------------------------------------------"
        )
        app.logger.debug("Framework: %s, version %s", manifest['fmw_name'], manifest['fmw_version'])
        app.logger.debug(
            "--------------------------------------------------------------------------------"
        )

        # Application configuration in log
        app.logger.info("Configuration file searched in %s", [cfg_file])
        app.logger.info("Configuration files found: %s", found_cfg_files)
        app.logger.info("Application settings: %s", app.config)

        if args['<command>'] == 'start':
            # Initialize backend communication ...
            frontend.configure(app.config.get('ui.backend', 'http://localhost:5000'))
            app.logger.info("Backend used: %s", frontend.url_endpoint_root)

            # Configure users' management backend
            User.set_backend(frontend)

            # Application current directory
            app_dir = os.path.abspath(os.path.dirname(__file__))

            # Load application plugins
            plugins = Plugins(app)
            plugins_dir = os.path.join(
                os.path.join(app_dir, manifest['name'].lower()),
                app.config.get('ui.plugins_dir', 'plugins')
            )
            plugins.load_plugins(plugins_dir)

            app.run(
                host=app.config['HOST'],
                port=app.config['PORT'],
                debug=app.config['DEBUG']
            )
    except Exception as e:
        print("Command '%s' failed, exception: %s / %s", args['<command>'], type(e), str(e))
        app.logger.error("failed to launch command '%s'", args['<command>'])
        app.logger.error("Back trace of this kill: %s", traceback.format_exc())
        sys.exit(3)

if __name__ == "__main__":
    main()
