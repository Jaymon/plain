# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import

from bs4.element import NavigableString
import requests

from ..base import Base, Soup
from .tag import Attributes


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
        return Soup(self.body["content"])

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



