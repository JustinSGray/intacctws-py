"""
Python client for Intacct Web Services API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

from pkg_resources import get_distribution, DistributionNotFound

try:
    d = get_distribution('intacct')
    __author__ = d.author
    __version__ = d.version
    __license__ = d.license
    __copyright__ = 'Copyright 2013, ' + __author__
except DistributionNotFound:
    # this should only occur during development
    # when the package is not installed.
    pass

from .api import IntacctApi
from .objfactory import ObjectFactory
from .objcache import ObjectCache
