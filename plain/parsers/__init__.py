# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import
import re
from collections import defaultdict
from urlparse import urlparse
import os

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
    def base_url(self):
        """Returns the base host of the url so http://foo.com/bar would return http://foo.com"""
        o = urlparse(self.url)
        scheme = o.scheme
        netloc = o.netloc
        return "{}://{}".format(scheme, netloc)

    @property
    def soup(self):
        # https://www.crummy.com/software/BeautifulSoup/
        # docs: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
        # bs4 codebase: http://bazaar.launchpad.net/~leonardr/beautifulsoup/bs4/files
        # TODO -- static cache this? All parsing instances will use it, could
        # keep a dict with url key and soup value. Probably not actually since
        # each parser can change it
        soup = BeautifulSoup(self.html, "html.parser")
        return soup

    def __init__(self, url, html):
        self.url = url
        self.html = html

    def parse(self):
        ret_html = ""
        self.article = self.find()
        self.clean()
        ret_html = self.article.prettify()
        return ret_html

    def find(self):
        # find p1, move to closest parent div, count <p>s, the div that has the
        # most child divs wins

        # go through all p tags, travel up until you find parent div, place parent
        # div in dict with counter, div that has the highest count wins, you will have
        # to go all the way up to the last parent to make sure there isn't a different
        # div that encompasses the found div, every div encountered gets a 
        soup = self.soup

        parents_d = defaultdict(lambda: dict(count=0, instance=None, children=set()))
        for tag in soup.find_all("p"):
            children = set([id(tag)])
            for parent in tag.parents:
                if parent.name not in set(["p", "body", "html"]):
                    key = id(parent)
                    parents_d[key]["count"] += 1
                    parents_d[key]["key"] = key
                    parents_d[key]["instance"] = parent
                    parents_d[key]["children"] |= children
                    children.add(key)

        # alright, now we wind the parent with the most p tags
        most_d = {"count": 0}
        for key, pd in parents_d.items():
            if pd["count"] > most_d["count"]:
                most_d = pd

            elif pd["count"] == most_d["count"]:
                if most_d["key"] not in pd["children"]:
                    most_d = pd


        if most_d["count"] > 0:
            el = most_d["instance"]

        return el


    def clean(self):
        # remove unwanted elements
        element = self.article
        for ename in ["script", "iframe", "form", "input", "textarea", "button", "aside"]:
            # TODO account for instagram and youtube embeds
            tag = element.find(ename)
            while tag:
                tag.decompose()
                tag = element.find(ename)

        tag = element
        while tag:
            if not isinstance(tag, NavigableString):
                attr = Attributes(tag)
                attr.clean()
            tag = tag.next_element

        for tag in element.find_all("img"):
            tag["src"] = self.absolute_url(tag["src"])

    def absolute_url(self, href):
        absolute_url = href
        if not re.match(r"^\S+:\/\/", href) and not href.startswith("data:"):
            if href.startswith("/"):
                absolute_url = "{}{}".format(self.base_url, href)

            else:
                hp = href
                if not hp.startswith("."):
                    hp = "./{}".format(hp)

                o = urlparse(self.url)
                path = os.path.normpath("{}{}".format(o.path, hp))
                absolute_url = urlparse.urlunparse(
                    o.scheme,
                    o.netloc,
                    path,
                    o.params,
                    o.query,
                    o.fragment
                )

        return absolute_url


class Article(Generic):
    def find(self):
        soup = self.soup
        el = soup.find("article")
        if el:
            header = el.find("header")
            if header:
                header.decompose()

            footer = el.find("footer")
            if footer:
                footer.decompose()

        return el


class MicroData(Generic):
    """Handles schema.org pages, currently supports Article and BlogPosting

    http://schema.org/
    http://schema.org/Article
    http://schema.org/BlogPosting
    """
    def find(self):
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

        return el


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

