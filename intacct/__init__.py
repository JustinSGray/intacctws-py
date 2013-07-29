"""
Intacct
~~~~~~~

Python client for Intacct API

:copyright: (c) 2013 by Jon Nalley
:license: see LICENSE for more details.

"""

__title__ = 'intacct'
__version__ = '0.0.1'
__author__ = 'Jon Nalley'
__email__ = 'code@bluebot.org'
__license__ = 'MIT'
__copyright__ = 'Copyright 2013, ' + __author__

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import json
from urlparse import urljoin
from requests.sessions import Session
from intacct.request import *

class IntacctApi(Session):
    api_url = 'https://api.intacct.com/ia/xml/xmlgw.phtml'

    def __init__(self, **kwargs):
        super(IntacctApi, self).__init__()
        self.headers.update({'Content-Type': 'x-intacct-xml-request'})
        self.InacctRequest = IntacctRequest(**kwargs)

    def getAPISession(self):
        """
        Obtain a sessionid and endpoint to be used for subsequent
        requests.
        """
        xml_request = self.InacctRequest.getAPISession()
        r = self.post(self.api_url, data=xml_request)
        xml = ET.fromstring(r.text)
        sessionid = getattr(xml.find('operation/result/data/api/sessionid'), 'text')
        endpoint = getattr(xml.find('operation/result/data/api/endpoint'), 'text')
        if sessionid and endpoint:
            self.api_url = endpoint
            self.InacctRequest.set_session_id(sessionid)
            return True
        raise Exception('Call to getAPISession failed:\n%s' % r.text)

    def readMore(self, obj):
        xml_request = self.InacctRequest.readMore(obj)
        r = self.post(self.api_url, data=xml_request)
        xml = ET.fromstring(r.text)
        data = xml.find('operation/result/data')
        return data

    def readByQuery(self, *args, **kwargs):
        """
        Read records using a query.

        Arguments:
        obj            - The name of object upon which to run the query

        Keyword arguments:
        query          - The query string to execute.  Use SQL operators
        fields         - A comma separated list of fields to return
        pagesize       - The number of records to return.  Defaults to 1000
        """
        # TODO: support returnFormat
        assert args
        obj = args[0]
        xml_request = self.InacctRequest.readByQuery(obj, **kwargs)
        r = self.post(self.api_url, data=xml_request)
        xml = ET.fromstring(r.text)
        data = xml.find('operation/result/data')
        remaining = int(data.attrib['numremaining'])
        while remaining > 0:
            newdata = self.readMore(obj)
            data.extend(newdata)
            remaining = int(newdata.attrib['numremaining'])
        return data
