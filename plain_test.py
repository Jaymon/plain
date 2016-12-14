# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import
from unittest import TestCase as BaseTestCase
import codecs
import os
from collections import defaultdict
import logging
import sys

import testdata

from plain import Article, Table


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


class ArticleTest(TestCase):
    def test_article(self):
        html = self.get_html("medium.com")
        a = Article("https://m.signalvnoise.com/best-buy-vs-the-apple-store-abb16cf342c0", html)
        path = testdata.create_file("foo.html", a.plain_html)
        # TODO -- test by length of plain html, that way if they change I can be alerted?
        # TODO -- how about stripping all tags and making sure first and last words are
        # correct, or title and sentence are there
        pout.v(path)

    def test_microdata(self):
        html = self.get_html("microdata_article")
        a = Article("http://argbash.readthedocs.io/en/stable/guide.html", html)
        path = testdata.create_file("foo.html", a.plain_html)

        html = self.get_html("microdata_blog")
        a = Article("http://blog.schema.org/2014/09/schemaorg-support-for-bibliographic_2.html", html)
        path = testdata.create_file("foo.html", a.plain_html)
        pout.v(path)

    def test_generic(self):
        html = self.get_html("businessinsider.com")
        a = Article("http://www.businessinsider.com/lularoe-is-making-millennial-moms-rich-2016-9", html)
        path = testdata.create_file("foo.html", a.plain_html)
        pout.v(path)

    def test_wordpress(self):
        html = self.get_html("newyorker.com")
        a = Article(
            "http://www.newyorker.com/magazine/2016/12/19/gawkers-demise-and-the-trump-era-threat-to-the-first-amendment",
            html
        )
        path = testdata.create_file("foo.html", a.plain_html)
        pout.v(path)

    def test_bloomberg(self):
        html = self.get_html("bloomberg.com")
        a = Article(
            "https://www.bloomberg.com/news/articles/2013-04-24/how-many-hft-firms-actually-use-twitter-to-trade",
            html
        )
        path = testdata.create_file("foo.html", a.plain_html)
        pout.v(path)

class TableTest(TestCase):
    def test_table(self):
        """This is really here to generate the table, not so much to actually test anything"""
        html = self.get_html("attributes")
        t = Table("https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes", html)

        r = defaultdict(list)
        for d in t.data:
            elements = d["Elements"].split(",")
            for el in elements:
                r[el.strip("<> ")].append(d["Attribute Name"])

        for attr in ["class", "contenteditable", "data-*", "draggable", "id", "style", "tabindex"]:
            r["Global attribute"].remove(attr)
        #ga = r.pop("Global attribute")
        #for k in r:
        #    r[k].append(ga)
        t.data = r
        print(t.pretty())

