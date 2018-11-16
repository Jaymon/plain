# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import
import re
from collections import defaultdict
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
        soup = BeautifulSoup(self.body, "html.parser")
        return soup

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
        return json.dumps(self.fields, sort_keys=True, indent=4)


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


class Article(Base):

# code to choose a parser based on url
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

    @property
    def soup(self):
        # https://www.crummy.com/software/BeautifulSoup/
        # docs: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
        # bs4 codebase: http://bazaar.launchpad.net/~leonardr/beautifulsoup/bs4/files
        soup = BeautifulSoup(self.body["content"], "html.parser")
        return soup

    def _simplify(self):
        """simplify what was returned from requests

        :param response: a requests response object
        """
        soup = self.soup
        self.simplify_document(soup)
        self.simplify_tags(soup)
        self.simplify_attrs(soup)
        #self.fields["content"] = soup.prettify(formatter=self.simplify_strings)

        fields = {key: self.body[key] for key in self.body if key != "content"}
        fields["content"] = soup.prettify(formatter=None)
        return fields

#     def simplify_strings(self, s):
#         pout.v(s)
#         return s

    def simplify_document(self, element):
        """simplify the structure of the document, by default this just gets rid of
        top level <div> and <article> elements so we basically have one level of <p>

        :param element: the beautiful soup [document] root
        """
        #pout.v(element.name)
        #pout.v(element.contents[0].name)
        if element.name == "[document]":
            contents = element.contents
            if len(contents) == 1:
                self.simplify_structure(element.contents[0])

#             while len(element.contents) == 1 and element.contents[0].name in ["div", "article"]:
#                 pout.v(element.contents[0].name)
#                 el = element.contents[0]
#                 el.unwrap()
# 
#         pout.v(len(element.contents), [el.name for el in element.contents])
        return element

    def simplify_structure(self, element):
        """The recursive method simpilify_document uses to get rid of stuff"""
        if not element: return
        if not element.name in ["div", "article"]: return

        contents = []
        for el in element.contents:
            if el.name is None:
                # we have a string
                if not el.string.isspace():
                    contents.append(el)

            else:
                contents.append(el)

        #pout.v(element.name, len(contents), [el.name for el in contents])

        if len(contents) == 1:
            self.simplify_structure(contents[0])

        #pout.v("unwrapping")
        element.unwrap()

    def simplify_tags(self, element):
        # remove tags get completely removed from the tree, strings and all
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

        # unwrapped tags are removed but strings between <tag> and </tag> are kept
        unwrap_tags = [
            "span",
            "meta"
        ]
        for ename in unwrap_tags:
            tag = element.find(ename)
            while tag:
                tag.unwrap()
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


class Mercury(Article):
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

    def _parse(self, response):
        d = response.json()
        return d


class Table(Base):
    """
    https://developer.mozilla.org/en-US/docs/Web/HTML/Element/table
    """
    def _simplify(self):
        # http://stackoverflow.com/questions/11790535/extracting-data-from-html-table
        datasets = {"tables": [], "dls": []}
        soup = self.soup
        datasets["tables"] = self.find_tables(soup)
        datasets["dls"] = self.find_dls(soup)
        return datasets

    def find_dimensions(self, table):
        """Return the col, row of the table

        straigh from the spec how to get column count:
        https://www.w3.org/TR/html4/struct/tables.html#h-11.2.4.3

        :param table: BeautifulSoup Element
        :returns: tuple, (rows, cols) = (int, int)
        """
        cols_x = 0
        rows_y = 0

        # https://developer.mozilla.org/en-US/docs/Web/HTML/Element/colgroup
        elem = table.find("colgroup", recursive=False)
        if elem:
            cols_x = elem.get("span", 1)
            col_elems = elem.find_all("col")
            if col_elems:
                cols_x = 0
                for col_elem in col_elems:
                    cols_x += int(col_elem.get("span", 1))

        thead = table.find("thead", recursive=False)
        if thead:
            tbody = table.find("tbody", recursive=False)
            tfoot = table.find("tfoot", recursive=False)
            for elem in [thead, tbody, tfoot]:
                if elem:
                    rows_y = max(len(elem.find_all("tr", recursive=False)), rows_y)

        if not cols_x:
            if thead:
                for tr in thead.find_all("tr", recursive=False):
                    for th in tr.find_all("th", recursive=False):
                        cols_x += int(th.get("colspan", 1))

                for elem in [tbody, tfoot]:
                    for tr in thead.find_all("tr", recursive=False):
                        td_cols_x = 0
                        for td in tr.find_all("td", recursive=False):
                            td_cols_x += int(td.get("colspan", 1))
                    cols_x = max(cols_x, td_cols_x)

            else:
                for tr in table.find_all("tr", recursive=False):
                    td_cols_x = 0
                    for name in ["td", "th"]:
                        for td in tr.find_all(name, recursive=False):
                            td_cols_x += int(td.get("colspan", 1))
                        cols_x = max(cols_x, td_cols_x)

        if not rows_y:
            rows_y = len(table.find_all("tr", recursive=False))

        return int(cols_x), int(rows_y)

    def find_headers(self, table):

        def get_ths(elem, cols_x):
            rows = []
            for y, tr in enumerate(elem.find_all("tr", recursive=False)):
                ths = tr.find_all("th", recursive=False)
                if not ths: break

                # if we are in a row that has normal columns it isn't a header
                # column so we're done
                tds = tr.find_all("td", recursive=False)
                if tds: break

                if len(ths) < cols_x:
                    rows.append([None] * cols_x)
                    xx = 0
                    x = 0
                    while xx < cols_x:
                        th = ths[x]
                        xy = y - 1
                        add = True
                        while xy >= 0:
                            if rows[xy][xx]:
                                rowspan = int(rows[xy][xx].get("rowspan", 0))
                                if (xy + rowspan - 1) >= y:
                                    add = False
                                    break
                            xy -= 1

                        if add:
                            rows[y][xx] = th
                            colspan = int(th.get("colspan", 1))
                            if colspan > 1:
                                for c in range(1, colspan):
                                    xx += 1
                                    rows[y][xx] = th

                            x += 1

                        xx += 1

                else:
                    rows.append(ths)

            return rows

        cols_x, rows_y = self.find_dimensions(table)
        thead = table.find("thead", recursive=False)
        if thead:
            rows = get_ths(thead, cols_x)
        else:
            rows = get_ths(table, cols_x)

        headers = [str(i) for i in range(1, cols_x + 1)]
        if rows:
            for x in range(cols_x):
                hs = []
                for row in rows:
                    if row[x]:
                        hs.append(row[x].get_text())

                headers[x] = " ".join(hs)

        return headers

    def find_content(self, table):
        rows = []
        cols_x, rows_y = self.find_dimensions(table)
        tbody = table.find("tbody", recursive=False)
        elems = []
        if tbody:
            tfoot = table.find("tfoot", recursive=False)
            elems = [tbody, tfoot]
        else:
            elems = [table]

        for elem in elems:
            if elem:
                trs = elem.find_all("tr", recursive=False)
                for tr in trs:
                    is_content_row = False
                    maybe_cols = tr.children
                    cols = []
                    for col in maybe_cols:
                        if col.name == "th":
                            cols.append(col)
                        elif col.name == "td":
                            is_content_row = True
                            cols.append(col)

                    if is_content_row:
                        rows.append([])
                        y = len(rows) - 1
                        for col in cols:
                            #rows[y].append(col.prettify())
                            rows[y].append(col.get_text())
                            colspan = int(col.get("colspan", 1))
                            if colspan > 1:
                                rows[y].extend([None] * colspan)

                        if len(rows[y]) < cols_x:
                            rows[y].extend([None] * (cols_x - len(rows[y])))

        return rows

    def find_table(self, table):
        ret = []
        headings = self.find_headers(table)
        content = self.find_content(table)
        for cols in content:
            columns = zip(headings, cols)
            d = {v[0]: v[1] for v in columns}
            ret.append(d)

        return ret

    def find_tables(self, soup):
        ret = []
        for table in soup.find_all("table"):
            r = self.find_table(table)
            ret.append(r)

        return ret

    def find_dls(self, soup):
        ret = []
        for dl in soup.find_all("dl"):
            rows = []
            terms = []
            #pout.v(list(dl.descendants))
            for el in dl.descendants:
                if el.name == "dt":
                    terms.append(el.get_text(strip=True))

                elif el.name == "dd":
                    rows.append({
                        "terms": terms,
                        "definition": el.get_text(strip=True)
                    })
                    terms = []

            ret.append(rows)

        return ret

