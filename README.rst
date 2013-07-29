intacctws-py
============

A Python interface to the Intacct Web Services API.

Installation
------------

To install intacctws-py simply:

.. code-block:: bash

    $ sudo pip install intacct

or alternatively (you really should be using pip though):

.. code-block:: bash

    $ sudo easy_install intacct

or from source:

.. code-block:: bash

    $ sudo python setup.py install

Getting Started
---------------

.. code-block:: pycon

    >>> from intacct import IntacctApi
    >>> i = IntacctApi(
    ...         senderid='mysenderid',
    ...         senderpass='mysenderpass',
    ...         userid='myuserid',
    ...         userpass='myuserpass',
    ...         companyid='mycompanyid'
    ...     )
    >>> i.getAPISession()
    ... True
    >>> result = i.readByQuery('USERINFO', )
    >>> for LOGINID in result.iter('LOGINID'):
    ...     print LOGINID.text
    ...
    FredFlintstone
    WilmaFlintstone
    BarneyRubble
    BettyRubble
    >>>

Limitations
-----------

This module is under development and much of the functionality provided by
the API is not yet supported.

- 'returnFormat' is not supported in readByQuery()
