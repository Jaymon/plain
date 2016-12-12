# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import
import re

from bs4 import BeautifulSoup, element
from bs4.element import NavigableString

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


class Generic(object):
    @property
    def soup(self):
        # https://www.crummy.com/software/BeautifulSoup/
        # docs: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
        # bs4 codebase: http://bazaar.launchpad.net/~leonardr/beautifulsoup/bs4/files
        # TODO -- static cache this? All parsing instances will use it, could
        # keep a dict with url key and soup value
        soup = BeautifulSoup(self.html, "html.parser")
        return soup

    def __init__(self, url, html):
        self.url = url
        self.html = html

    def parse(self):
        # find p1, move to closest parent div, count <p>s, the div that has the
        # most child divs wins
        raise NotImplementedError()

    def clean(self, element):
        tag = element
        while tag:
            if not isinstance(tag, NavigableString):
                attr = Attributes(tag)
                attr.clean()
            tag = tag.next_element


class Article(Generic):
    def parse(self):
        ret_html = ""
        soup = self.soup
        el = soup.find("article")
        if el:
            header = el.find("header")
            if header:
                header.decompose()

            footer = el.find("footer")
            if footer:
                footer.decompose()

            self.clean(el)
            ret_html = el.prettify()
            #pout.v(el)

        return ret_html


class MicroData(Generic):
    """Handles schema.org pages, currently supports Article and BlogPosting

    http://schema.org/
    http://schema.org/Article
    http://schema.org/BlogPosting
    """
    def parse(self):
        ret_html = ""
        soup = self.soup
        el = soup.find("div", {"itemtype": "http://schema.org/Article"})
        if not el:
            el = soup.find("div", {"itemtype": "http://schema.org/BlogPosting"})

        if el:
            # we need to make sure the schema isn't bogus and actually contains the
            # body of the post
            regex = re.compile("articleBody")
            tag = el.find("div", {"itemprop": regex})
            if not tag:
                tag = el.find("p", {"itemprop": regex})

            if tag:
                # get rid of any micro data meta tags
                # for some reason I can't use find_all() and have the tags actually remove
                tag = el.find("meta")
                while tag:
                    tag.decompose()
                    tag = el.find("meta")
                #for tag in el.find_all("meta"):
                #    tag.decompose()

                self.clean(el)
                ret_html = el.prettify()

        return ret_html


# class TitleInfer(Generic):
#     """This will try and discover the body by looking for <h1>, <h2>, or <h3> tag"""
#     def parse(self):
#         ret_html = ""
#         soup = self.soup
#         el = soup.find("div", {"itemtype": "http://schema.org/Article"})


class Table(Generic):
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

