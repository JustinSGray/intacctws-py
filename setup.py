#!/usr/bin/env python

from setuptools import setup

__title__ = 'intacct'
__version__ = '0.0.1'
__author__ = 'Jon Nalley'
__email__ = 'code@bluebot.org'
__license__ = 'MIT'
__copyright__ = 'Copyright 2013, ' + __author__

def doc(name):
    with open(name) as f:
        return f.read()

setup(
    name=__title__,
    version=__version__,
    description='Python client for Intacct API',
    long_description=doc('README.rst'),
    url='https://github.com/jnalley/intacctws-py',
    author=__author__,
    author_email=__email__,
    license=__license__,
    packages=[
        'intacct',
    ],
    install_requires=[
        'requests',
    ],
    zip_safe=False
)
