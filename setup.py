#!/usr/bin/env python

from setuptools import setup
from intacct import __title__,__version__,__license__,__author__,__email__

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
