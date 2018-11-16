# -*- coding: utf-8 -*-
from __future__ import absolute_import

from .version import is_py2, is_py3

if is_py2:
    import urlparse as parse

elif is_py3:
    from urllib import parse

