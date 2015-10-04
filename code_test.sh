#!/usr/bin/env bash
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

echo 'pep8 ...'
pep8 --max-line-length=100 --exclude='*.pyc, *.cfg' --ignore='E402' app.py alignak_webui/*
echo 'pylint ...'
pylint --rcfile=.pylintrc alignak_webui/
echo 'pep157 ...'
pep257 --select=D300 alignak_webui
echo 'tests ...'
cd test
nosetests -xv --process-restartworker --processes=1 --process-timeout=300 --with-coverage --cover-package=alignak_webui test*.py
echo 'coverage combine ...'
coverage combine
coverage report -m
cd ..