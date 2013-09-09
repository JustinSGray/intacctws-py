#!/usr/bin/env python

from setuptools import setup
from intacct import \
    __title__,  \
    __author__,  \
    __version__, \
    __license__


def doc(name):
    with open(name) as f:
        return f.read()

setup(
    name=__title__,
    version=__version__,
    author=__author__,
    author_email='code@bluebot.org',
    license=__license__,
    url='https://github.com/jnalley/intacctws-py',
    description='Python client for Intacct API',
    long_description=doc('README.rst'),
    packages=[
        'intacct',
    ],
    package_data={
        '': ['LICENSE'],
    },
    install_requires=[
        'requests',
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ]
)
