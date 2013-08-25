try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from weakref import WeakKeyDictionary
from .objcache import ObjectCache


def _conditional_setattr(self, key, value):
    """
    This method insures that only attributes which were set during class
    creation by IntacctMetaclass are settable.
    """
    if not hasattr(self, key):
        raise RuntimeError("Invalid attribute '%s' for objects of type '%s'" %
                           (key, self.__class__.__name__))
    object.__setattr__(self, key, value)


def _toxml(el, o):
    """
    Create XML by recursing through the object
    """
    for attr in dir(o):
        if attr.startswith('_'):
            continue
        value = getattr(o, attr)
        if not value:
            continue
        if type(value) != str:
            _toxml(ET.SubElement(el, value.__class__.__name__), value)
        else:
            ET.SubElement(el, attr).text = value


def _tostring(self):
    """
    Convert object to an XML string
    """
    el = ET.Element(self._object_name)
    _toxml(el, self)
    return ET.tostring(el)


class ObjectDescriptor(object):
    def __init__(self):
        self.data = WeakKeyDictionary()

    def __get__(self, instance, owner):
        # print "(__get__) instance: %s, owner: %s" % (instance, owner)
        return self.data.get(instance)

    def __set__(self, instance, value):
        # print "(__set__) instance: %s, value: %s" % (instance, value)
        self.data[instance] = value


class IntacctMetaclass(type):
    """
    Metaclass for creating an IntacctClass
    """
    def __new__(cls, name, cache, bases, dct):
        properties = cache.get(name)
        if not properties:
            raise RuntimeError("Object type '%s' not found in cache" % name)
        for prop, propval in properties.iteritems():
            if type(propval) is not dict:
                continue
            if propval.get('_nested'):
                attributes = {'__setattr__': _conditional_setattr}
                for aname, aval in propval.iteritems():
                    attributes[aname] = ObjectDescriptor()
                dct[prop] = type(prop, (), attributes)()
            else:
                dct[prop] = ObjectDescriptor()
        dct['__setattr__'] = _conditional_setattr
        dct['__str__'] = _tostring
        dct['_object_name'] = properties['_object_name']
        return super(IntacctMetaclass, cls).__new__(cls, name, bases, dct)


def ObjectFactory(typename, **kwargs):
    """
    Factory for creating Intacct objects
    """
    cache = ObjectCache()
    return IntacctMetaclass.__new__(
        IntacctMetaclass, typename, cache, (object,), dict(**kwargs)
    )()
