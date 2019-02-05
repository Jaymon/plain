# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import
import bs4
#from bs4 import BeautifulSoup, Tag
import requests


class SoupMixin(object):
    def inner_html(self):
        # https://stackoverflow.com/a/18602241/5006
        return self.decode_contents()
        #return self.decode_contents(formatter="html")
        #return col.renderContents(prettyPrint=True)


class SoupTag(bs4.Tag, SoupMixin):
    pass


class Soup(bs4.BeautifulSoup, SoupMixin):
    """Small wrapper around Beautiful Soup that picks the best parser

    this is a modified version of the Soup class found in brow.utils
    """
    # https://bazaar.launchpad.net/~leonardr/beautifulsoup/bs4/view/head:/bs4/__init__.py
    # https://www.crummy.com/software/BeautifulSoup/
    # docs: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
    # bs4 codebase: http://bazaar.launchpad.net/~leonardr/beautifulsoup/bs4/files
    def __init__(self, markup="", features=None, *args, **kwargs):
        # https://www.crummy.com/software/BeautifulSoup/bs4/doc/#parser-installation
        if not features:
            features = "html.parser"
            try:
                import lxml
                features = "lxml"

            except ImportError:
                try:
                    import html5lib
                    features = "html5lib"

                except ImportError:
                    pass

        super(Soup, self).__init__(markup, features, *args, **kwargs)

#     def new_tag(self, name, namespace=None, nsprefix=None, attrs={}, **kwattrs):
#         """Create a new tag associated with this soup."""
#         pout.h()
#         kwattrs.update(attrs)
#         return self.tag_class(None, self.builder, name, namespace, nsprefix, kwattrs)


# !!! I don't love this but it does work, it allows me to use my child class
# throughout beautifulsoup (4.7.1), I figure if I am doing something that uses Plain I
# won't mind having bs4 overridden like this since I will be in the "Plain"
# environment anyway
bs4.Tag = SoupTag

