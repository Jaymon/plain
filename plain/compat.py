# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import
import sys

# shamelessly ripped from https://github.com/kennethreitz/requests/blob/master/requests/compat.py
# Syntax sugar.
_ver = sys.version_info
is_py2 = (_ver[0] == 2)
is_py3 = (_ver[0] == 3)


if is_py2:
    basestring = basestring
    range = xrange # range is now always an iterator

    # shamelously ripped from six https://bitbucket.org/gutworth/six
    exec("""def reraise(tp, value, tb=None):
        try:
            raise tp, value, tb
        finally:
            tb = None
    """)

    from HTMLParser import HTMLParser
    import urlparse as parse
    from StringIO import StringIO
    unescape = HTMLParser.unescape


elif is_py3:
    basestring = (str, bytes)

    # ripped from six https://bitbucket.org/gutworth/six
    def reraise(tp, value, tb=None):
        try:
            if value is None:
                value = tp()
            if value.__traceback__ is not tb:
                raise value.with_traceback(tb)
            raise value
        finally:
            value = None
            tb = None

    from html.parser import HTMLParser
    from urllib import parse
    from io import StringIO

    try:
        from html import unescape
    except ImportError:
        unescape = HTMLParser.unescape

# TODO using reraise

#             if py_2:
#                 #raise error_info[0].__class__, error_info[0], error_info[1][2]
#                 reraise(*error_info)
#                 #raise error_info[0].__class__, error_info[1], error_info[2]
# 
#             elif py_3:
#                 #e, exc_info = error_info
#                 #et, ei, tb = exc_info
# 
#                 reraise(*error_info)
#                 #et, ei, tb = error_info
#                 #raise ei.with_traceback(tb)


# if not error_info:
#                     exc_info = sys.exc_info()
#                     #raise e.__class__, e, exc_info[2]
#                     #self.error_info = (e, exc_info)
#                     self.error_info = exc_info
# 
# if error_info:
# 
#             reraise(*error_info)

String = unicode if is_py2 else str
Bytes = str if is_py2 else bytes

