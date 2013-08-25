#!/usr/bin/env python

import intacct
from setuptools import setup

def doc(name):
    with open(name) as f:
        return f.read()

setup(
    name='intacct',
    version='0.0.3',
    author='Jon Nalley',
    author_email='code@bluebot.org',
    license='MIT',
    url='https://github.com/jnalley/intacctws-py',
    description='Python client for Intacct API',
    long_description=doc('README.rst'),
    packages=[
        'intacct',
    ],
    install_requires=[
        'requests',
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
    ]
)
