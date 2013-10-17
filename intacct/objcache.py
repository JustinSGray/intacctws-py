try:
    import cPickle as pickle
except ImportError:
    import pickle

import os.path
from .api import IntacctApi
from .default import cache_file, cache_objects


FIXUP_FIELDS = {
    'USERINFO': {
        'SSO_ENABLED': {
            'externalDataName': 'boolean',
            'isReadOnly': 'false',
            'isRequired': 'false',
            'maxLength': '0'
        },
        'SSO_FEDERATED_ID': {
            'externalDataName': 'string',
            'isReadOnly': 'false',
            'maxLength': '200'
        },
        'SSO_COMPANY_ENABLED': {
            'externalDataName': 'string',
            'isReadOnly': 'false',
            'isRequired': 'false',
            'maxLength': '0'
        },
    }
}


def fixup(cache):
    """
    Unfortunately inspect does not return all the fields
    for the USERINFO object.  This function adds the missing
    single sign on fields.
    """
    cache['USERINFO'].update(FIXUP_FIELDS['USERINFO'])


class ObjectCache(dict):
    def __init__(self, cache_dir=None):
        cache_dir = cache_dir or os.path.expanduser("~")
        self.path = os.path.join(cache_dir, cache_file)
        cache = {}
        if os.path.exists(self.path):
            with open(self.path, 'r') as cachefile:
                cache = pickle.loads(cachefile.read())
        super(ObjectCache, self).__init__(cache)

    def dump(self):
        """
        A debug function to display the cache contents.
        """
        from pprint import PrettyPrinter
        pp = PrettyPrinter(indent=4)
        pp.pprint(self)

    def initialize(self, api):
        """
        This method creates a data structure formed by calling 'inspect' on the
        'cache_objects' and writes it to 'cache_file' in the home directory of
        the current user.  This data structure is used to create helper classes
        for creating new objects.
        """
        assert isinstance(api, IntacctApi), \
            "ObjectCache requires IntacctApi instance for initialization"
        self.clear()
        cache = {}
        # required = []
        wanted = ['externalDataName', 'isReadOnly', 'isRequired', 'maxLength']
        for item in cache_objects:
            xml = api.inspect(name=item, detail=1)
            objname = xml.find('operation/result/data/Type').attrib['Name']
            elements = xml.findall('operation/result/data/Type/Fields/Field')
            for fields in elements:
                if objname not in cache:
                    cache[objname] = {}
                p = cache[objname]
                # field_name = None
                for field in fields:
                    if field.tag == 'Name':
                        # field_name = field.text
                        if '.' in field.text:
                            y = p
                            for e in field.text.split('.'):
                                if e not in y:
                                    y[e] = {'_nested': True}
                                y = y[e]
                        else:
                            if field.text not in p:
                                p[field.text] = {}
                            y = p[field.text]
                    elif field.tag and field.text and field.tag in wanted:
                        if field.tag == 'isRequired' and field.text == 'true':
                            # required.append(field_name)
                            pass
                        else:
                            y[field.tag] = field.text
            # cache[objname]['__required__'] = required
            cache[objname]['_object_name'] = objname
            cache[item] = cache[objname]
        fixup(cache)
        with open(self.path, 'w') as cachefile:
            pickle.dump(cache, cachefile)
        super(ObjectCache, self).__init__(cache)
