# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import
import re
from collections import defaultdict
from urlparse import urlparse
import os
import json

from bs4 import BeautifulSoup, element
from bs4.element import NavigableString
import requests

from .data import ATTRIBUTES


class Attributes(object):
    @property
    def supported(self):
        attrs = ATTRIBUTES.get(self.element.name, [])
        attrs.extend(ATTRIBUTES["Global attribute"])
        return set(attrs)

    def __init__(self, element):
        self.element = element

    def clean(self):
        supported = self.supported
        for attr in self.element.attrs.keys():
            if attr not in supported:
                del self.element[attr]


class Base(object):
    @property
    def soup(self):
        # https://www.crummy.com/software/BeautifulSoup/
        # docs: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
        # bs4 codebase: http://bazaar.launchpad.net/~leonardr/beautifulsoup/bs4/files
        soup = BeautifulSoup(self.fields["content"], "html.parser")
        return soup

    def __init__(self, url):
        self.url = url

    def fetch(self):
        res = self._fetch()
        if res.status_code >= 400:
            raise IOError("Problem fetching {}, code {}".format(self.url, res.status_code))

        return self.simplify(res)

    def _fetch(self):
        raise NotImplementedError()


    def simplify(self, response):
        """simplify what was returned from requests

        :param response: a requests response object
        """
        self.fields = self._simplify(response) # keep the api consistent for the future

        soup = self.soup
        self.simplify_tags(soup)
        self.simplify_attrs(soup)
        #self.fields["content"] = soup.prettify(formatter=self.simplify_strings)
        self.fields["content"] = soup.prettify(formatter=None)

    def _simplify(self, response):
        """handle converting the requests response to a nice dictionary

        :param response: a requests response instance from a HTTP request
        :returns: a dictionary containing keys like 'content'
        """
        raise NotImplementedError()

    def json(self):
        """returns this instance as a nicely formatted json string"""
        return json.dumps(self.fields, sort_keys=True, indent=4)

    def simplify_strings(self, s):
        pout.v(s)
        return s

    def simplify_tags(self, element):
        remove_tags = [
            "script",
            "iframe",
            "form",
            "input",
            "textarea",
            "button",
            "aside",
        ]
        for ename in remove_tags:
            # TODO account for instagram and youtube embeds?
            tag = element.find(ename)
            while tag:
                tag.decompose()
                tag = element.find(ename)

        return element

    def simplify_attrs(self, element):
        for tag in element:
            while tag:
                if not isinstance(tag, NavigableString):
                    attr = Attributes(tag)
                    attr.clean()
                tag = tag.next_element
                #tag = tag.next


class Mercury(Base):
    """Wrapper class around Readability's mercury parsing api

    https://mercury.postlight.com

    a response typically looks like this:

        {
            'domain': u"example.com",
            'rendered_pages': 1,
            'author': u"...",
            'url': u"https://example.com/some/permalink",
            'excerpt': u"...",
            'title': u"...",
            'lead_image_url': u"https://example.com/some/image.jpg",
            'direction': u"ltr",
            'word_count': 1145,
            'total_pages': 1,
            'content': "..."
            'date_published': u"2013-04-24T00:00:00.000Z",
            'dek': None,
            'next_page_url': None
        }
    """
    def _fetch(self):
        headers = {
            "x-api-key": os.environ["PLAIN_MERCURY_KEY"],
        }
        params = {
            "url": self.url
        }

        return requests.get(
            "https://mercury.postlight.com/parser",
            params=params,
            headers=headers
        )

    def _simplify(self, response):
        d = response.json()
        return d












class Table(Base):
    def parse(self):
        # http://stackoverflow.com/questions/11790535/extracting-data-from-html-table
        datasets = []
        soup = self.soup
        # TODO -- make this go through all tables in html
        table = soup.find("table")

        # The first tr contains the field names.
        headings = [th.get_text() for th in table.find("tr").find_all("th")]

        for row in table.find_all("tr")[1:]:
            dataset = zip(headings, (td.get_text() for td in row.find_all("td")))
            d = {v[0]: v[1] for v in dataset}
            datasets.append(d)

        return datasets

