# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import
import json

import requests

from ..soup import Soup


class Base(object):
    """It's the idea that all the various parsers will inherit from this class"""
    @property
    def soup(self):
        return Soup(self.body)

    def __init__(self, url, body=None):
        self.url = url
        self.body = body

    def parse(self):
        """This is the public facing method where all the magic happens, instantiate
        an instance of a subclass and then call this method

        :returns: a dict of values pulled from the url including "content" key
        """
        if self.body is None:
            res = self.fetch()
            self.body = self._parse(res)

        self.simplify()

        return self.fields

    def _parse(self, response):
        """Given a response object return what you want this class's body to contain"""
        return response.content

    def fetch(self):
        """If you don't pass body into the init method then you will need to go and
        get it, that's what this method does

        :returns: requests.Response
        """
        res = self._fetch()
        if res.status_code >= 400:
            raise IOError("Problem fetching {}, code {}".format(self.url, res.status_code))

        return res

    def _fetch(self):
        return requests.get(self.url)

    def simplify(self):
        """simplify what was returned from requests"""
        self.fields = self._simplify()

    def _simplify(self):
        """handle converting the requests response to a nice dictionary

        :returns: whatever you want in self.fields
        """
        raise NotImplementedError()

    def json(self):
        """returns this instance as a nicely formatted json string"""
        # https://coderwall.com/p/gmxnqg/pretty-printing-a-python-dictionary
        return json.dumps(self.fields, sort_keys=True, indent=4)

