"""
intacct.api
~~~~~~~~~~~~

This module implements the Intacct API.

"""

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from requests.sessions import Session
from .request import IntacctRequest
from .default import api_url


class IntacctApi(object):
    def __init__(self, **kwargs):
        """
        Constructor for API instance.

        Keyword arguments:
            senderid    The registered Web Services ID provided to you by
                        Intacct.
            senderpass  The registered Web Services Password.
            userid      Your registered Intacct User ID.
            userpass    This is your registered password.
            companyid   Specifies the user's company.
        """
        self.api_url = api_url
        self.connection = Session()
        self.connection.headers.update(
            {'Content-Type': 'x-intacct-xml-request'}
        )
        self.request = IntacctRequest(**kwargs)

    def get_api_session(self):
        """
        Obtain a sessionid and endpoint to be used for subsequent
        requests.
        """
        xml_request = self.request.get_api_session()
        r = self.connection.post(self.api_url, data=xml_request)
        xml = ET.fromstring(r.text)
        sessionid = getattr(
            xml.find('operation/result/data/api/sessionid'),
            'text'
        )
        endpoint = getattr(
            xml.find('operation/result/data/api/endpoint'),
            'text'
        )
        if sessionid and endpoint:
            self.api_url = endpoint
            self.request.set_session_id(sessionid)
            return True
        raise Exception('Call to get_api_session() failed:\n%s' % r.text)

    def create(self, *args):
        """
        The create method is used to create one or more records.  Currently,
        the system limits the user to creating 100 records in a single create
        call.  Records of different types can be created in a single call to
        the create method.
        """
        xml_request = self.request.create(*args)
        r = self.connection.post(self.api_url, data=xml_request)
        xml = ET.fromstring(r.text)
        return xml

    def delete(self, *args):
        """
        The delete method is used to delete one or more records.  Currently,
        the system limits the user to deleting 100 records in a single call.

        This function accepts either an object string and a list of keys or a
        list of tuples in the form:

            [
                ('object1', [ 'key1', 'key2', ... ] ),
                ('object2', [ 'key1', 'key2', ... ] ),
                ...
            ]
        """
        xml_request = self.request.delete(*args)
        r = self.connection.post(self.api_url, data=xml_request)
        xml = ET.fromstring(r.text)
        return xml

    def inspect(self, **kwargs):
        """
        The inspect method is used to get a list of all the fields and their
        attributes for an object. This method can also be used to get a list
        of available objects.

        Keyword arguments:
            obj       The integration name of the object to inspect. Must be
                      passed unless the name argument is used. Pass "*" to get
                      the entire list of objects.

            name      The record name of the object to inspect. Must be passed
                      unless the object argument is used. Pass "*" to get the
                      entire list of objects.

            detail    Optional. Specify the detail level. Setting this value to
                      '1' will additionally retrieve field level attributes. By
                      default, the method will simply return a list of fields.
                      This is an attribute on the inspect element.
        """
        xml_request = self.request.inspect(**kwargs)
        r = self.connection.post(self.api_url, data=xml_request)
        xml = ET.fromstring(r.text)
        return xml

    def read_more(self, obj):
        xml_request = self.request.read_more(obj)
        r = self.connection.post(self.api_url, data=xml_request)
        xml = ET.fromstring(r.text)
        data = xml.find('operation/result/data')
        return data

    def read_by_query(self, *args, **kwargs):
        """
        Read records using a query.

        Arguments:
        obj            - The name of object upon which to run the query

        Keyword arguments:
        query          - The query string to execute.  Use SQL operators
        fields         - A comma separated list of fields to return
        pagesize       - The number of records to return.
        """
        assert args
        obj = args[0]
        xml_request = self.request.read_by_query(obj, **kwargs)
        r = self.connection.post(self.api_url, data=xml_request)
        xml = ET.fromstring(r.text)
        data = xml.find('operation/result/data')
        remaining = int(data.attrib['numremaining'])
        while remaining > 0:
            newdata = self.read_more(obj)
            data.extend(newdata)
            remaining = int(newdata.attrib['numremaining'])
        return data
