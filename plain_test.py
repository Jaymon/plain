# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import
from unittest import TestCase as BaseTestCase
import codecs
import os
from collections import defaultdict
import logging
import sys
import json

from bs4 import BeautifulSoup
import testdata

from plain import Article, Table, Url
from plain.parsers.html.article import Mercury
#from plain.parsers.html.table import Headers


# configure root logger
testdata.basic_logging()
# logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)
# log_handler = logging.StreamHandler(stream=sys.stderr)
# log_formatter = logging.Formatter('[%(levelname).1s] %(message)s')
# log_handler.setFormatter(log_formatter)
# logger.addHandler(log_handler)


class TestCase(BaseTestCase):
    def get_html(self, filename):
        basepath = os.path.abspath(os.path.expanduser(os.path.dirname(__file__)))
        path = os.path.join(basepath, "testdata", "html", "{}.html".format(filename))
        with codecs.open(path, encoding='utf-8', mode='r') as f:
            html = f.read()
        return html

    def get_json(self, filename):
        basepath = os.path.abspath(os.path.expanduser(os.path.dirname(__file__)))
        path = os.path.join(basepath, "testdata", "json", "{}.json".format(filename))

        with codecs.open(path, encoding='utf-8', mode='r') as f:
            body = json.load(f)
        return body

    def get_soup(self, filename):
        html = self.get_html(filename)
        soup = BeautifulSoup(self.body, "html.parser")
        return soup


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
        pout.v(m)

    def test_fetch_bi(self):
        m = self.get_patched("businessinsider.com")
        m.fetch()
        pout.v(m)

    def test_fetch_newyorker(self):
        filename = "newyorker.com"
        m = self.get_patched(filename)
        m.fetch()
        pout.v(m)

    def test_fetch_medium(self):
        filename = "signalvnoise.com"
        m = self.get_patched(filename)
        m.fetch()
        pout.v(m)

    def test_fetch_bespoke(self):
        filename = "twistedmatrix.com"
        m = self.get_patched(filename)
        m.fetch()
        pout.v(m)

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


class TableTest(TestCase):
    def test_dimensions(self):
        html = self.get_html("tables4")
        t = Table(testdata.get_url(), html)

        tables = t.soup.find_all("table")

        cols, rows = t.find_dimensions(tables[2])
        self.assertEqual((4, 3), (cols, rows))

        cols, rows = t.find_dimensions(tables[3])
        self.assertEqual((3, 2), (cols, rows))

        cols, rows = t.find_dimensions(tables[1])
        self.assertEqual((2, 1), (cols, rows))

        cols, rows = t.find_dimensions(tables[5])
        self.assertEqual((6, 2), (cols, rows))


        html = self.get_html("tables3")
        t = Table(testdata.get_url(), html)
        cols, rows = t.find_dimensions(t.soup.find_all("table")[1])
        self.assertEqual((3, 55), (cols, rows))

    def test_content(self):
        html = self.get_html("tables4")
        t = Table(testdata.get_url(), html)
        tables = t.soup.find_all("table")
        tests = {
            0: [
                {
                    'Last name': {
                        "headers": [],
                        "value": "Doe",
                    },
                    'First name':  {
                        "headers": [],
                        "value": "John"
                    }
                },
                {
                    'Last name': {
                        "headers": [],
                        "value":  "Doe",
                    },
                    'First name':  {
                        "headers": [],
                        "value": "Jane"
                    }
                }
            ],
            1: [
                {
                    'Header content 1': {
                        "headers": [],
                        "value": "Body content 1",
                    },
                    'Header content 2': {
                        "headers": [],
                        "value": "Body content 2"
                    },
                },
                {
                    'Header content 1': {
                        "headers": [],
                        "value": "Footer content 1",
                    },
                    'Header content 2': {
                        "headers": [],
                        "value": "Footer content 2"
                    },
                }
            ],
            6: [
                {
                    'header 2': {
                        "headers": [],
                        "value": "Content 1.2",
                    },
                    'header 1': {
                        "headers": [],
                        "value": "Content 1.1"
                    },
                },
                {
                    'header 2': {
                        "headers": [],
                        "value": "Content 2.2",
                    },
                    'header 1': {
                        "headers": [],
                        "value": "Content 2.1"
                    },
                }
            ]
        }

        for i, r in tests.items():
            ret = t.find_table(tables[i])
            self.assertEqual(r, ret["rows"])

#         html = self.get_html("tables3")
#         t = Table(testdata.get_url(), html)
#         ret = t.find_content(t.soup.find_all("table")[1])
#         pout.v(ret)


#     def test_tables2(self):
#         url = "https://en.wikipedia.org/wiki/Web_colors"
#         html = self.get_html("tables2")
#         t = Table(url, html)
#         tables = t.soup.find_all("table")
#         for table in tables:
#             pout.v(table.prettify())
#             pout.v(t.find_table(table))
#             pout.b(5)

#     def test_tables3(self):
#         url = "https://en.wikipedia.org/wiki/Web_colors"
#         html = self.get_html("tables3")
#         t = Table(url, html)
#         t.parse()

    def test_dl(self):
        url = testdata.get_url()


        html = "\n".join([
            "<dl>",
            "  <dt>term1</dt>",
            "  <dd>definition 1</dd>",
            "  <dt>term2</dt>",
            "  <dd>definition 2</dd>",
            "</dl>",
            "<dl>",
            "  <dt>term3</dt>",
            "  <dd>definition 3</dd>",
            "  <dt>term4</dt>",
            "  <dd>definition 4</dd>",
            "</dl>",
        ])
        t = Table(url, html)
        t.parse()
        self.assertEqual(2, len(t.fields["dls"]))
        self.assertEqual(2, len(t.fields["dls"][0]))
        self.assertEqual(2, len(t.fields["dls"][1]))

        html = "\n".join([
            "<dl>",
            "  <dt>term1</dt>",
            "  <dt>term2</dt>",
            "  <dd>definition 1</dd>",
            "  <dt>term3</dt>",
            "  <dd>definition 2</dd>",
            "</dl>",
        ])

        t = Table(url, html)
        t.parse()
        self.assertEqual(1, len(t.fields["dls"]))
        self.assertEqual(2, len(t.fields["dls"][0]))

    def test_dl_full(self):
        url = "https://developer.mozilla.org/en-US/docs/Web/HTML/Block-level_elements"
        html = self.get_html("tables")

        t = Table(url, html)
        t.parse()
        self.assertEqual(4, len(t.fields["dls"]))


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

    def test_tables6(self):
        html = self.get_html("tables6")
        t = Table(testdata.get_url(), html)
        t.parse()

        self.assertEqual(5, len(t.fields["tables"][0]["rows"]))

        for row in t.fields["tables"][0]["rows"]:
            self.assertEqual(4, len(row))

        for v in ["1 header", "1 subheader"]:
            for row in t.fields["tables"][0]["rows"][0].values():
                self.assertTrue(v in row["headers"])

        for v in ["2 header", "2 subheader"]:
            for row in t.fields["tables"][0]["rows"][1].values():
                self.assertTrue(v in row["headers"])

        for v in ["2 header", "3 subheader"]:
            for row in t.fields["tables"][0]["rows"][2].values():
                self.assertTrue(v in row["headers"])

        for v in ["4 header", "4 subheader"]:
            for row in t.fields["tables"][0]["rows"][3].values():
                self.assertTrue(v in row["headers"])

    def test_row_th(self):
        """This was one of the test tables in the docs, it has a td in the header
        row and a th in the content row, the parser needs to handle these cases

        this was my original note:
            we need to make sure it can parse a table that has a th and td in the same tr
        """
        html = [
            '<table>',
            '    <tr>',
            '        <td> </td>',
            '        <th scope="col">Batman</th>',
            '        <th scope="col">Robin</th>',
            '        <th scope="col">The Flash</th>',
            '        <th scope="col">Kid Flash</th>',
            '    </tr>',
            '    <tr>',
            '        <th scope="row">Skill</th>',
            '        <td>Smarts</td>',
            '        <td>Dex, acrobat</td>',
            '        <td>Super speed</td>',
            '        <td>Super speed</td>',
            '    </tr>',
            '</table>',
        ]
        t = Table(testdata.get_url(), "\n".join(html))
        t.parse()

        result = {
            '0': {
                "headers": [],
                "value": "Skill",
            },
            'Batman':  {
                "headers": [],
                "value": "Smarts"
            },
            'Robin': {
                "headers": [],
                "value":  "Dex, acrobat",
            },
            'The Flash':  {
                "headers": [],
                "value": "Super speed"
            },
            'Kid Flash':  {
                "headers": [],
                "value": "Super speed"
            }
        }
        self.assertEqual(result, t.tables[0]["rows"][0])


    def test_no_headers(self):
        html = [
            "<table>",
            "    <tr>",
            "        <td>Column 1</td>",
            "        <td>Column 2</td>",
            "        <td>Column 3</td>",
            "        <td>Column 4</td>",
            "    </tr>",
            "</table>",
        ]
        t = Table(testdata.get_url(), "\n".join(html))
        t.parse()

        result = {
            '0': {
                "headers": [],
                "value": "Column 1",
            },
            '1': {
                "headers": [],
                "value": "Column 2",
            },
            '2': {
                "headers": [],
                "value": "Column 3",
            },
            '3': {
                "headers": [],
                "value": "Column 4",
            },
        }
        self.assertEqual(result, t.tables[0]["rows"][0])


class UrlTest(TestCase):
    def test_utm(self):
        original_url = "https://example.com/path/?utm_source=source&utm_campaign=campaign-source&utm_medium=medium&utm_term=blah-blah-blah"
        plain_url = Url(original_url)
        self.assertEqual("https://example.com/path/", plain_url)

        original_url = "https://example.com/path/?utm_source=source&foo=bar"
        plain_url = Url(original_url)
        self.assertEqual("https://example.com/path/?foo=bar", plain_url)

        original_url = "https://example.com/path/#anchor"
        plain_url = Url(original_url)
        self.assertEqual("https://example.com/path/", plain_url)

