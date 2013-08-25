"""
Default values used in other modules
"""

# Intacct gateway URL
api_url = 'https://api.intacct.com/ia/xml/xmlgw.phtml'
# Default page size
page_size = 1000
# Maximum page size
max_page_size = 100000
# A list of objects that will be 'inspected' and
# whose meta data will be stored.  This cache is used
# to implement helper classes for creating these types
# of objects.
cache_objects = ['User', 'User Role']
# Name of cache file.
cache_file = '.intacct.cache'
