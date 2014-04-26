#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='pgextras',
    version='0.1.0',
    description="Unofficial Python port of Heroku's pgextras that provides"
                " various statistics for a Postgres instance.",
    long_description=readme + '\n\n' + history,
    author='Scott Woodall',
    author_email='scott.woodall@gmail.com',
    url='https://github.com/scottwoodall/python-pgextras',
    packages=[
        'pgextras',
    ],
    package_dir={'pgextras':
                 'pgextras'},
    include_package_data=True,
    install_requires=[
    ],
    license="BSD",
    zip_safe=False,
    keywords='pgextras',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
    test_suite='tests',
)
