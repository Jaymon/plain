# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import
import logging
import json
import urllib
import hashlib

import requests

from .compat.urllib import parse
from . import parsers


logger = logging.getLogger(__name__)


__version__ = "0.0.1"

"""
order of operations of parsers:

    1 - plugin of the hostname, so arstechnica.com would first search for ArstechnicaCom
    2 - Article plugin that will search for an article tag
    3 - generic that will parse based on found plain text outside of tags
    4 - if all else fails, fallback to third party parser?

Also, on the url, should I strip the #anchor and utm_* params? I say yes, I would need to
compensate for #! hashbanging though if that is still a thing (I might be showing my age)

Whichever one is chosen, the html should be stripped of class, id, and style attributes
"""

class Base(object):

    def __init__(self, original_url, original_html=""):
        self.original_url = original_url
        self.original_html = original_html
#         if original_html:
#             self.original_html = original_html
#         else:
#             self.original_html = self.fetch_html()
        self.simplify()

#     def fetch_html(self):
#         kwargs = {}
#         res = requests.get(self.original_url, **kwargs)
#         if res.status_code >= 400:
#             raise IOError("Problem fetching {}, code {}".format(self.original_url, res.status_code))
# 
#         return res.content

    def simplify(self):
        raise NotImplementedError()


class Article(Base):

    @property
    def parser(self):
        return parsers.Mercury
#         ps = []
#         if self.original_url:
#             o = parse.urlparse(self.original_url)
#             host = o.hostname
#             bits = host.split(".")
#             class_name = "".join((b.lower().title() for b in bits))
#             klass = getattr(parsers, class_name, None)
#             if klass:
#                 ps.append(klass)
# 
#         ps.append(parsers.Article)
#         ps.append(parsers.MicroData)
#         ps.append(parsers.Generic)
#         return ps

    def simplify(self):
        parser = self.parser
        p = parser(self.original_url)
        self.fields = p.parse()

    def __getattr__(self, key):
        return self.fields[key]


class Table(Base):
    def simplify(self):
        p = parsers.Table(self.original_url)
        self.data = p.parse()

    def pretty(self):
        # https://coderwall.com/p/gmxnqg/pretty-printing-a-python-dictionary
        return json.dumps(self.data, sort_keys=True, indent=4)


class Url(str):
    """Take a url and strip any gunk from it"""

    @classmethod
    def parse_query(cls, query):
        if not query: return {}

        d = {}
        for k, kv in parse.parse_qs(query, True, strict_parsing=True).items():
            if len(kv) > 1:
                d[k] = kv
            else:
                d[k] = kv[0]

        return d

    @classmethod
    def unparse_query(cls, query_kwargs):
        if not query_kwargs: return ""
        return urllib.urlencode(query_kwargs, doseq=True)

    @classmethod
    def simplify(cls, original_url):
        data = {
            "original_url": original_url,
        }

        o = parse.urlparse(original_url)

        query_kwargs = {}
        query = o.query
        if query:
            query_kwargs = cls.parse_query(query)
            query_kwargs = {k: v for k, v in query_kwargs.items() if not k.startswith("utm_")}

        #query = cls.unparse_query(query_kwargs) if query_kwargs else ""
        data["query_kwargs"] = query_kwargs
        data["scheme"] = o.scheme
        data["netloc"] = o.netloc
        data["path"] = o.path

        data["plain_url"] = parse.urlunsplit((
            data["scheme"],
            data["netloc"],
            data["path"],
            cls.unparse_query(data["query_kwargs"]),
            ""
        ))
        return data

    def __new__(cls, original_url):
        data = cls.simplify(original_url)

        instance = super(Url, cls).__new__(cls, data.pop("plain_url"))
        for k, v in data.items():
            setattr(instance, k, v)
        return instance

    def hash(self):
        """return an md5 hash of the url"""
        return hashlib.md5(self).hexdigest()

