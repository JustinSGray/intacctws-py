try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from collections import OrderedDict
from .default import page_size, max_page_size

"""
Class for forming Intacct XML requests
"""


class IntacctRequest(object):
    def __init__(self, **kwargs):
        """
        IntacctRequest Constructor
        """
        self.sessionid = False
        self.create_control_element(**kwargs)
        self.create_login_element(**kwargs)

    def set_session_id(self, sessionid=None):
        """
        Set a sessionid.  If sessionid is set
        requests will be made using the sessionid
        rather than authenticating with a username
        and password.
        """
        self.sessionid = sessionid or False

    def validate_control_credentials(self, **kwargs):
        """
        Validate the control credentials
        """
        dtdversion = kwargs.get('dtd') or '3.0'
        self.controlid = kwargs.get('controlid') or 'foobar'
        uniqueid = kwargs.get('uniqueid') or False
        assert 'senderid' in kwargs
        assert 'senderpass' in kwargs
        assert dtdversion in ('3.0', '2.1')
        assert uniqueid in (True, False)
        return OrderedDict([
            ('senderid', kwargs.get('senderid')),
            ('password', kwargs.get('senderpass')),
            ('controlid', self.controlid),
            ('uniqueid', str(uniqueid).lower()),
            ('dtdversion', dtdversion),
        ])

    def validate_login_credentials(self, **kwargs):
        """
        Validate the login credentials
        """
        assert 'companyid' in kwargs
        assert 'userid' in kwargs
        assert 'userpass' in kwargs
        return OrderedDict([
            ('userid', kwargs.get('userid')),
            ('companyid', kwargs.get('companyid')),
            ('password', kwargs.get('userpass')),
        ])

    def create_control_element(self, **kwargs):
        """
        Create the control element
        """
        credentials = self.validate_control_credentials(**kwargs)
        # build control element
        self.control = ET.Element('control')
        for key, value in credentials.iteritems():
            ET.SubElement(self.control, key).text = value

    def create_login_element(self, **kwargs):
        """
        Create the login element
        """
        credentials = self.validate_login_credentials(**kwargs)
        self.login = ET.Element('login')
        for key, value in credentials.iteritems():
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
        function = ET.SubElement(content, 'function', {
            'controlid': self.controlid
        })
        return root, function

    def get_api_session(self):
        root, function = self.create_request()
        ET.SubElement(function, 'getAPISession')
        return ET.tostring(root)

    def create(self, *args):
        assert args
        assert len(args) <= 100
        root, function = self.create_request()
        create = ET.SubElement(function, 'create')
        for obj in args:
            create.append(obj)
        return ET.tostring(root)

    def delete(self, *args):
        assert args
        items = type(args[0]) is list and args[0] or [args]
        assert len(items) <= 100
        root, function = self.create_request()
        for obj, keys in items:
            delete = ET.SubElement(function, 'delete')
            ET.SubElement(delete, 'object').text = obj
            ET.SubElement(delete, 'keys').text = ','.join(keys)
        return ET.tostring(root)

    def inspect(self, **kwargs):
        obj = kwargs.get('obj')
        name = kwargs.get('name')
        detail = kwargs.get('detail')
        assert obj or name, "'obj' or 'name' is required"
        root, function = self.create_request()
        inspect = ET.SubElement(function, 'inspect')
        if detail:
            inspect.attrib['detail'] = str(detail)
        if obj:
            assert not name, "only one of 'obj' or 'name' may be specified"
            ET.SubElement(inspect, 'object').text = obj
        else:
            ET.SubElement(inspect, 'name').text = name
        return ET.tostring(root)

    def read_more(self, obj):
        root, function = self.create_request()
        el = ET.SubElement(function, 'readMore')
        ET.SubElement(el, 'object').text = obj
        return ET.tostring(root)

    def read_by_query(self, obj, **kwargs):
        assert obj
        pagesize = kwargs.get('pagesize') or page_size
        pagesize = pagesize <= max_page_size and pagesize or page_size
        root, function = self.create_request()
        el = ET.SubElement(function, 'readByQuery')
        ET.SubElement(el, 'object').text = obj
        ET.SubElement(el, 'fields').text = kwargs.get('fields') or '*'
        ET.SubElement(el, 'query').text = kwargs.get('query') or ''
        ET.SubElement(el, 'returnFormat').text = 'xml'
        ET.SubElement(el, 'pagesize').text = str(pagesize)
        return ET.tostring(root)
