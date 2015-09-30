#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
del os.link
from importlib import import_module

try:
    from setuptools import setup, find_packages
except:
    sys.exit("Error: missing python-setuptools library")

try:
    python_version = sys.version_info
except:
    python_version = (1, 5)
if python_version < (2, 7):
    sys.exit("This application requires a minimum Python 2.7.x, sorry!")
elif python_version >= (3,):
    sys.exit("This application is not yet compatible with Python 3.x, sorry!")

from alignak_webui import __application__, settings, __version__, __copyright__, __releasenotes__, __license__, __doc_url__
# package = __import__('alignak_webui')
package = import_module('alignak_webui')

# print find_packages()
# print __license__
# sys.exit(1)

setup(
    name="Alignak_WebUI",
    version=__version__,

    license=__license__,

    # metadata for upload to PyPI
    author="Frédéric MOHIER",
    author_email="frederic.mohier@gmail.com",
    keywords="alignak monitoring web ui",
    url="https://github.com/mohierf/webui",
    description=package.__doc__.strip(),
    long_description=open('README.rst').read(),

    zip_safe=False,

    packages=find_packages(),
    include_package_data=True,

    install_requires=['configparser', 'requests', 'Flask', 'docopt', 'alignak_backend_client'],

    entry_points={
        'console_scripts': [
            'alignak_webui = alignak_webui.__main__:main',
        ],
    },

    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'Intended Audience :: Customer Service',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Systems Administration'
    ]
)
