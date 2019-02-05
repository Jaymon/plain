# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import

from ..base import Soup
from ...compat import String, HTMLParser, unescape


# http://stackoverflow.com/a/925630/5006
# https://docs.python.org/2/library/htmlparser.html
class HTMLCleaner(HTMLParser):
    """strip html tags from a string
    :example:
        html = "this is <b>some html</b>
        text = HTMLStripper.strip_tags(html)
        print(text) # this is some html
    """

    # https://developer.mozilla.org/en-US/docs/Web/HTML/Block-level_elements
    BLOCK_TAGNAMES = set([
        "address",
        "article",
        "aside",
        "blockquote",
        "br",
        "canvas",
        "dd",
        "div",
        "dl",
        "fieldset", "figcaption",
        "figure",
        "footer",
        "form",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "header", 
        "hgroup", 
        "hr",
        "li",
        "main",
        "nav",
        "noscript",
        "ol",
        "output",
        "p",
        "pre",
        "section",
        "table",
        "tfoot",
        "ul",
        "video",
    ])

    @classmethod
    def strip_tags(cls, html, *args, **kwargs):
        s = cls(*args, **kwargs)
        # convert entities back otherwise stripper will get rid of them
        # http://stackoverflow.com/a/28827374/5006
        #html = s.unescape(html)
        s.feed(html)
        return s.get_data()

    def __init__(self, block_sep="\n", inline_sep="", img_as_data=False):
        self.reset()
        self.fed = []
        self.block_sep = block_sep
        self.inline_sep = inline_sep
        self.img_as_data = img_as_data
        super(HTMLCleaner, self).__init__()

    def handle_data(self, d):
        self.fed.append(d)

    def handle_entityref(self, name):
        self.fed.append("&{};".format(name))

    def handle_starttag(self, tag, attrs):
        # https://docs.python.org/3/library/html.parser.html#html.parser.HTMLParser.handle_starttag
        if tag == "img" and self.img_as_data:
            for attr_name, attr_val in attrs:
                if attr_name == "src":
                    self.fed.append("\n{}\n".format(attr_val))

    def handle_endtag(self, tagname):
        if tagname in self.BLOCK_TAGNAMES:
            if self.block_sep:
                self.fed.append(self.block_sep)
        else:
            if self.inline_sep:
                self.fed.append(self.inline_sep)

    def get_data(self):
        return "".join(self.fed)

    @classmethod
    def unescape(cls, html):
        """unescapes html entities (eg, &gt;) to plain text (eg, &gt; becomes >)"""
        # https://stackoverflow.com/a/2087433/5006
        return unescape(html)


class HTML(String):
    """Converts html to plaintext but still allows access to the original html
    through the .html property"""
    @property
    def soup(self):
        return Soup(self.html)

    @property
    def unescaped_html(self):
        return HTMLCleaner.unescape(self.html)

    def __new__(cls, html, keep_images=False):
        s = HTMLCleaner.strip_tags(html, img_as_data=keep_images).strip()
        instance = super(HTML, cls).__new__(cls, s)
        instance.html = html
        return instance

