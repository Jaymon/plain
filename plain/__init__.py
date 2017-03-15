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


class Article(parsers.Mercury):
    def __getattr__(self, key):
        return self.fields[key]


class Table(parsers.Table):
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

