#!/usr/bin/env python
# encoding: utf-8

#
# The MIT License (MIT)
#
# Copyright (c) 2013-2014 Camille GUINAUDEAU
# Copyright (c) 2013-2014 Hervé BREDIN (http://herve.niderb.fr/)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

SERIES_NAME = 'GameOfThrones'

import versioneer
versioneer.versionfile_source = '{name}/_version.py'.format(name=SERIES_NAME)
versioneer.versionfile_build = '{name}/_version.py'.format(name=SERIES_NAME)
versioneer.tag_prefix = ''
versioneer.parentdir_prefix = '{name}-'.format(name=SERIES_NAME)


from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

setup(
    name='TVD{name}'.format(name=SERIES_NAME),
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="{name} plugin for TVD dataset".format(name=SERIES_NAME),
    author="Herve Bredin",
    author_email="bredin@limsi.fr",
    packages=find_packages(),
    package_data={
        SERIES_NAME: ['{name}.yml'.format(name=SERIES_NAME)]
    },
    include_package_data=True,
    install_requires=[
        "tvd>=0.1.1",
        "urllib3>=1.7"
    ],
    entry_points="""
        [tvd.series]
        {name}={name}:{name}
    """.format(name=SERIES_NAME)
)
