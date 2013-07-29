try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from collections import OrderedDict

"""
Class for creating Intacct API requests
"""

_DEFAULT_PAGE_SIZE = 1000
_MAX_PAGE_SIZE = 100000

class IntacctRequest(object):
    sessionid = False
    credentials = { 'control': {}, 'login': {} }

    def __init__(self, **kwargs):
        """
        IntacctRequest Constructor
        """
        self.set_control_credentials(**kwargs)
        self.set_login_credentials(**kwargs)
        self.create_control_element()
        self.create_login_element()

    def set_session_id(self, sessionid):
        self.sessionid = sessionid

    def set_control_credentials(self, **kwargs):
        """
        Set the control credentials
        """
        dtdversion = kwargs.get('dtd') or '3.0'
        controlid = kwargs.get('controlid') or 'foobar'
        uniqueid = kwargs.get('uniqueid') or False
        assert 'senderid' in kwargs
        assert 'senderpass' in kwargs
        assert dtdversion in ('3.0', '2.1')
        assert uniqueid in (True, False)
        self.credentials['control'] = OrderedDict([
            ('senderid', kwargs.get('senderid')),
            ('password', kwargs.get('senderpass')),
            ('controlid', controlid),
            ('uniqueid', str(uniqueid).lower()),
            ('dtdversion', dtdversion),
        ])

    def set_login_credentials(self, **kwargs):
        """
        Set the login credentials
        """
        assert 'companyid' in kwargs
        assert 'userid' in kwargs
        assert 'userpass' in kwargs
        self.credentials['login'] = OrderedDict([
            ('userid', kwargs.get('userid')),
            ('companyid', kwargs.get('companyid')),
            ('password', kwargs.get('userpass')),
        ])

    def create_control_element(self):
        """
        Create the control element
        """
        # build control element
        self.control = ET.Element('control')
        for key,value in self.credentials['control'].iteritems():
            ET.SubElement(self.control, key).text = value

    def create_login_element(self):
        """
        Create the login element
        """
        self.login = ET.Element('login')
        for key,value in self.credentials['login'].iteritems():
            ET.SubElement(self.login, key).text = value

    def create_request(self):
        root = ET.Element('request')
        root.append(self.control)
        operation = ET.SubElement(root, 'operation')
        authentication = ET.SubElement(operation, 'authentication')
        if self.sessionid:
            ET.SubElement(authentication, 'sessionid').text = self.sessionid
        else:
            authentication.append(self.login)
        content = ET.SubElement(operation, 'content')
        function = ET.SubElement(content, 'function',
            { 'controlid': self.credentials['control']['controlid'] })
        return root, function

    def getAPISession(self):
        root, function = self.create_request()
        ET.SubElement(function, 'getAPISession')
        return ET.tostring(root)

    def readMore(self, obj):
        root, function = self.create_request()
        readByQuery = ET.SubElement(function, 'readMore')
        ET.SubElement(readByQuery, 'object').text = obj
        return ET.tostring(root)

    def readByQuery(self, obj, **kwargs):
        assert obj
        pagesize = kwargs.get('pagesize') or _DEFAULT_PAGE_SIZE
        assert pagesize <= _MAX_PAGE_SIZE
        root, function = self.create_request()
        readByQuery = ET.SubElement(function, 'readByQuery')
        ET.SubElement(readByQuery, 'object').text = obj
        ET.SubElement(readByQuery, 'fields').text = kwargs.get('fields') or '*'
        ET.SubElement(readByQuery, 'query').text = kwargs.get('query') or ''
        ET.SubElement(readByQuery, 'returnFormat').text = kwargs.get('returnFormat') or 'xml'
        ET.SubElement(readByQuery, 'pagesize').text = str(pagesize)
        return ET.tostring(root)
