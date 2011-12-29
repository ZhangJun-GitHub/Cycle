#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010-2011 Reality <tinmachin3@gmail.com> and Psychedelic Squid <psquid@psquid.net>
# Copyright (C) 2011 Matt Molyneaux <moggers87+git@moggers87.co.uk>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""
Standard build script.
"""

__docformat__ = 'restructuredtext'

import distutils
from setuptools import setup, find_packages

try:
    distutils.dir_util.remove_tree("build", "dist", "src/identicurse.egg-info")
except:
    pass

setup(
    name="cycle",
    version='3.9.9-dev',
    description="Calendar program for women",
    long_description=("""Cycle is a calendar for women. Given a cycle length or statistics
for several periods, it can calculate the days until \
menstruation, the fertile period, and the days to ovulations, \
and define the d.o.b. of a child. It allows the user to write \
notes and helps to supervise the administration of hormonal \
contraceptive tablets."""),
    author="Oleg S. Gint",
    maintainer="Matt Molyneaux"
    maintainer_email="moggers87+git@moggers87.co.uk"
    url="http://moggers.co.uk/cgit/cycle.git/about",
    download_url=("http://moggers.co.uk/cgit/cycle.git"),

    license="GPLv2+",

    data_files=[('cycle',['README', 'README.html'])],
    packages=['cycle'],
    package_dir={'cycle': 'src'},
    include_package_data=True,

    entry_points={
        'gui_scripts':
            ['cycle = cycle.main'],
    },

    classifiers=[
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
    ],
)
