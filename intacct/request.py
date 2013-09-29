try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import logging
log = logging.getLogger(__name__)
from requests.sessions import Session
from collections import OrderedDict
from .default import api_url


def ElementWithSubElements(name, d):
    e = ET.Element(name)
    for key, value in d.iteritems():
        ET.SubElement(e, key).text = value
    return e


def Credentials(**kwargs):
    """
    Validate Credentials
    """
    dtdversion = kwargs.get('dtd') or '3.0'
    uniqueid = kwargs.get('uniqueid') or False
    assert 'senderid' in kwargs
    assert 'senderpass' in kwargs
    assert dtdversion in ('3.0', '2.1')
    assert uniqueid in (True, False)
    assert 'companyid' in kwargs
    assert 'userid' in kwargs
    assert 'userpass' in kwargs
    control = OrderedDict([
        ('senderid', kwargs.get('senderid')),
        ('password', kwargs.get('senderpass')),
        ('controlid', kwargs.get('controlid') or 'foobar'),
        ('uniqueid', str(uniqueid).lower()),
        ('dtdversion', dtdversion),
    ])
    login = OrderedDict([
        ('userid', kwargs.get('userid')),
        ('companyid', kwargs.get('companyid')),
        ('password', kwargs.get('userpass')),
    ])
    return control, login


class IntacctRequest(object):
    """
    Create XML and post request
    """
    def __init__(self, **kwargs):
        self.url = api_url
        self.root = ET.Element('request')
        control, login = Credentials(**kwargs)
        self.controlid = control['controlid']
        self.root.append(ElementWithSubElements('control', control))
        operation = ET.SubElement(self.root, 'operation')
        self.authentication = ET.SubElement(operation, 'authentication')
        self.authentication.append(ElementWithSubElements('login', login))
        content = ET.SubElement(operation, 'content')
        self.function = ET.SubElement(content, 'function')
        self.connection = Session()
        self.connection.headers.update(
            {'Content-Type': 'x-intacct-xml-request'}
        )

    def set_session_id(self, sessionid, endpoint):
        self.authentication.clear()
        self.url = endpoint
        ET.SubElement(self.authentication, 'sessionid').text = sessionid

    def __call__(self, element):
        self.function.clear()
        self.function.attrib.update(controlid=self.controlid)
        self.function.append(element)
        xmltext = ET.tostring(self.root)
        log.debug("Request: %s", xmltext)
        r = self.connection.post(self.url, data=xmltext)
        log.debug("Response: %s", ' '.join(r.text.splitlines()))
        try:
            r.raise_for_status()
            xml = ET.fromstring(r.text)
            status = getattr(xml.find('operation/result/status'), 'text')
            if status == 'success':
                return xml
        except:
            pass
        raise Exception("Status: %d, Response: '%s'" % (
            r.status_code, r.text))
