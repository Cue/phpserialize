#!/usr/bin/env python
# Copyright 2010 Greplin, Inc.  All Rights Reserved.

"""Setup script for phpserialize."""

try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup

setup(name='phpserialize',
      version='1.0',
      description='PHP-compatible serialize and unserialize',
      license='Apache',
      author='Greplin, Inc.',
      author_email='opensource@greplin.com',
      url='http://www.github.com/Greplin/phpserialize',
      py_modules = ['phpserialize'],
      test_suite = 'tests',
)