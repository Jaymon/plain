# -*- coding: utf-8 -*-
from __future__ import absolute_import

from .version import is_py2, is_py3

if is_py2:
    from StringIO import StringIO

elif is_py3:
    from io import StringIO

