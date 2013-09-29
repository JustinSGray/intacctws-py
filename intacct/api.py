"""
intacct.api
~~~~~~~~~~~~

This module implements the Intacct API.

"""

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import logging
log = logging.getLogger(__name__)
from .request import IntacctRequest
from .default import page_size, max_page_size


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
        self.request = IntacctRequest(**kwargs)

    def get_api_session(self):
        """
        Obtain a sessionid and endpoint to be used for subsequent
        requests.
        """
        xml = self.request(ET.Element('getAPISession'))
        sessionid = getattr(
            xml.find('operation/result/data/api/sessionid'),
            'text'
        )
        endpoint = getattr(
            xml.find('operation/result/data/api/endpoint'),
            'text'
        )
        if sessionid and endpoint:
            self.request.set_session_id(sessionid, endpoint)
            log.debug(
                "Obtained session id: %s, Using endpoint: %s",
                sessionid, endpoint
            )
            return True
        raise Exception("Failed to find 'sessionid' and 'endpoint'")

    def create(self, *args):
        """
        The create method is used to create one or more records.  Currently,
        the system limits the user to creating 100 records in a single create
        call.  Records of different types can be created in a single call to
        the create method.
        """
        assert args
        assert len(args) <= 100
        create = ET.Element('create')
        for obj in args:
            if hasattr(obj, '_object_factory'):
                obj = obj()
            elif type(obj) is str:
                obj = ET.fromstring(obj)
            create.append(obj)
        self.request(create)
        return True

    def delete(self, object, *args):
        """
        The delete method is used to delete one or more records.  Currently,
        the system limits the user to deleting 100 records in a single call.
        """
        assert args
        assert len(args) <= 100
        delete = ET.Element('delete')
        ET.SubElement(delete, 'object').text = object
        ET.SubElement(delete, 'keys').text = ','.join(map(str, args))
        self.request(delete)
        return True

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
        obj = kwargs.get('obj')
        name = kwargs.get('name')
        detail = kwargs.get('detail')
        assert obj or name, "'obj' or 'name' is required"
        inspect = ET.Element('inspect')
        if detail:
            inspect.attrib['detail'] = str(detail)
        if obj:
            assert not name, "only one of 'obj' or 'name' may be specified"
            ET.SubElement(inspect, 'object').text = obj
        else:
            ET.SubElement(inspect, 'name').text = name
        return self.request(inspect)

    def read_more(self, obj):
        readmore = ET.Element('readMore')
        ET.SubElement(readmore, 'object').text = obj
        xml = self.request(readmore)
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
        pagesize = kwargs.get('pagesize') or page_size
        pagesize = pagesize <= max_page_size and pagesize or page_size
        readbyquery = ET.Element('readByQuery')
        ET.SubElement(readbyquery, 'object').text = obj
        ET.SubElement(readbyquery, 'fields').text = kwargs.get('fields') or '*'
        ET.SubElement(readbyquery, 'query').text = kwargs.get('query') or ''
        ET.SubElement(readbyquery, 'returnFormat').text = 'xml'
        ET.SubElement(readbyquery, 'pagesize').text = str(pagesize)
        xml = self.request(readbyquery)
        data = xml.find('operation/result/data')
        remaining = 0
        if data:
            remaining = int(data.attrib['numremaining'])
        while remaining > 0:
            newdata = self.read_more(obj)
            data.extend(newdata)
            remaining = int(newdata.attrib['numremaining'])
        return data
