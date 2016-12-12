# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import
from urlparse import urlparse
import logging
import json

import requests

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
        if original_html:
            self.original_html = original_html
        else:
            self.original_html = self.fetch_html()
        self.simplify()

    def fetch_html(self):
        kwargs = {}
        res = requests.get(self.original_url, **kwargs)
        if res.status_code >= 400:
            raise IOError("Problem fetching {}, code {}".format(self.original_url, res.status_code))

        return res.content

    def simplify(self):
        raise NotImplementedError()


class Article(Base):

    @property
    def parsers(self):
        ps = []
        if self.original_url:
            o = urlparse(self.original_url)
            host = o.hostname
            bits = host.split(".")
            class_name = "".join((b.lower().title() for b in bits))
            klass = getattr(parsers, class_name, None)
            if klass:
                ps.append(klass)

        ps.append(parsers.Article)
        ps.append(parsers.MicroData)
        ps.append(parsers.Generic)
        return ps

    def simplify(self):
        parsers = self.parsers
        for parser in parsers:
            p = parser(self.original_url, self.original_html)
            plain_html = p.parse()
            if plain_html:
                logger.debug("plain html from {}".format(parser))
                self.plain_html = plain_html
                break


class Table(Base):
    def simplify(self):
        p = parsers.Table(self.original_url, self.original_html)
        self.data = p.parse()

    def pretty(self):
        # https://coderwall.com/p/gmxnqg/pretty-printing-a-python-dictionary
        return json.dumps(self.data, sort_keys=True, indent=4)


