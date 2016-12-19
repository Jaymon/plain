# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import
from unittest import TestCase as BaseTestCase
import codecs
import os
from collections import defaultdict
import logging
import sys
import json

import testdata

from plain import Article, Table
from plain.parsers import Mercury


# configure root logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
log_handler = logging.StreamHandler(stream=sys.stderr)
log_formatter = logging.Formatter('[%(levelname).1s] %(message)s')
log_handler.setFormatter(log_formatter)
logger.addHandler(log_handler)



class TestCase(BaseTestCase):
    def get_html(self, filename):
        basepath = os.path.abspath(os.path.expanduser(os.path.dirname(__file__)))
        path = os.path.join(basepath, "testdata", "{}.html".format(filename))
        with codecs.open(path, encoding='utf-8', mode='r') as f:
            html = f.read()
        return html

    def get_json(self, filename):
        basepath = os.path.abspath(os.path.expanduser(os.path.dirname(__file__)))
        path = os.path.join(basepath, "testdata", "json", "{}.json".format(filename))

        with codecs.open(path, encoding='utf-8', mode='r') as f:
            body = json.load(f)
        return body


class MercuryParserTest(TestCase):
    def get_patched(self, filename):
        """this patches a Mercury instance with what the api would return"""
        fields = self.get_json(filename)
        url = fields["url"]
        m = Mercury(url)
        class MockResponse(object):
            status_code = 200
            def json(slf):
                return fields

        m_patched = testdata.patch(m, _fetch=lambda *args, **kwargs: MockResponse())
        return m_patched

    def cache_json(self, url, filename):
        m = Mercury(url)
        m.fetch()
        basepath = os.path.abspath(os.path.expanduser(os.path.dirname(__file__)))
        path = os.path.join(basepath, "testdata", "json", "{}.json".format(filename))

        with codecs.open(path, encoding='utf-8', mode='w+') as f:
            f.write(m.json())

        return m

    def test_fetch_bloomberg(self):
        m = self.get_patched("bloomberg.com")
        m.fetch()

    def test_fetch_bi(self):
        m = self.get_patched("businessinsider.com")
        m.fetch()

    def test_fetch_newyorker(self):
        filename = "newyorker.com"
        m = self.get_patched(filename)
        m.fetch()

    def test_fetch_medium(self):
        filename = "signalvnoise.com"
        m = self.get_patched(filename)
        m.fetch()

    def test_fetch_bespoke(self):
        filename = "twistedmatrix.com"
        m = self.get_patched(filename)
        m.fetch()

    def test_fetch_multipage(self):
        filename = "uproxx.com"
        m = self.get_patched(filename)
        m.fetch()
        pout.v(m.fields)

    def test_fetch_uproxx(self):
        filename = "uproxxpage.com"
        m = self.get_patched(filename)
        m.fetch()
        pout.v(m.fields)
        # uproxx should have a custom parser that looks for:
        # <div class="uproxx_mp_sidebar_item  active" data-type="page" data-page="5">
        # and adds that to the end of the url, so uproxx.com/.../5/ and requests that
        # url, that will allow Mercury to fetch the whole article.

#         m = self.cache_json(
#             "http://uproxx.com/news/standing-rock-protests-motivations-history-interview/5/",
#             filename
#         )
#         path = testdata.create_file("{}.html".format(filename), m.fields["content"])
#         pout.v(path)



    def xtest_fetch_foo(self):
        filename = ""
        m = self.cache_json(
            "http://www.businessinsider.com/lularoe-is-making-millennial-moms-rich-2016-9",
            filename
        )
        path = testdata.create_file("{}.html".format(filename), m.fields["content"])
        pout.v(path)


#         html = self.get_html("medium.com")
#         a = Article("https://m.signalvnoise.com/best-buy-vs-the-apple-store-abb16cf342c0", html)
#         path = testdata.create_file("foo.html", a.plain_html)
#         # TODO -- test by length of plain html, that way if they change I can be alerted?
#         # TODO -- how about stripping all tags and making sure first and last words are
#         # correct, or title and sentence are there
#         pout.v(path)


# class TableTest(TestCase):
#     def test_table(self):
#         """This is really here to generate the table, not so much to actually test anything"""
#         html = self.get_html("attributes")
#         t = Table("https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes", html)
# 
#         r = defaultdict(list)
#         for d in t.data:
#             elements = d["Elements"].split(",")
#             for el in elements:
#                 r[el.strip("<> ")].append(d["Attribute Name"])
# 
#         for attr in ["class", "contenteditable", "data-*", "draggable", "id", "style", "tabindex"]:
#             r["Global attribute"].remove(attr)
#         #ga = r.pop("Global attribute")
#         #for k in r:
#         #    r[k].append(ga)
#         t.data = r
#         print(t.pretty())
# 
