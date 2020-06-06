#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
#       Copyright (C) 2010, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the GNU General Public License (GPLv2 or later)
#                  http://www.gnu.org/licenses/
##############################################################################

import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='lmsremind',
      version='1.0',
      description='A scheduling and reminder program',
      license='GPLv2 or later',
      author='Joel B. Mohler',
      author_email='joel@kiwistrawberry.us',
      long_description=read('README.md'),
      url='https://github.com/jbmohler/lmsremind',
      scripts=['scripts/lmsremind'],
      packages=['remindlib'],
      install_requires='fuzzyparsers'
     )
