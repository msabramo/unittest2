#! /usr/bin/env python
# setup.py
# Install script for unittest2
# Copyright (C) 2010 Michael Foord
# E-mail: fuzzyman AT voidspace DOT org DOT uk

# This software is licensed under the terms of the BSD license.
# http://www.voidspace.org.uk/python/license.shtml

import os
from unittest2 import __version__ as VERSION

NAME = 'unittest2'

PACKAGES = ['unittest2', 'unittest2.test']
SCRIPTS = ['unit2.py', 'unit2']

DESCRIPTION = ('The new features in unittest for Python 2.7 backported to '
               'Python 2.4+.')

URL = 'http://pypi.python.org/pypi/unittest2'

readme = os.path.join(os.path.dirname(__file__), 'README.txt')
LONG_DESCRIPTION = open(readme).read()

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.4',
    'Programming Language :: Python :: 2.5',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Operating System :: OS Independent',
    'Topic :: Software Development :: Libraries',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Software Development :: Testing',
]

AUTHOR = 'Michael Foord'

AUTHOR_EMAIL = 'michael@voidspace.org.uk'

KEYWORDS = "unittest testing tests".split(' ')


params = dict(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=PACKAGES,
    scripts=SCRIPTS,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    classifiers=CLASSIFIERS,
    keywords=KEYWORDS
)

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
else:
    params.update(dict(
        entry_points = {
            'console_scripts': [
                'unit2 = unittest2:main_',
                ],
            },
    ))
    
    params['test_suite'] = 'unittest2.collector'

setup(**params)
