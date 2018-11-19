# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import

# TODO -- if I ever need a tld list, I can use the table parser on this:
# https://en.wikipedia.org/wiki/List_of_Internet_top-level_domains

# key = tagname, value = list of attributes supported
# common attributes are stored in "Global attribute" key
# generated using Table parser and https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes
ATTRIBUTES = {
    "Global attribute": [
        "accesskey",
        "contextmenu",
        "dir",
        "dropzone",
        "hidden",
        "itemprop",
        "lang",
        "spellcheck",
        "title"
    ],
    "a": [
        "download",
        "href",
        "hreflang",
        "media",
        "ping",
        "rel",
        "shape",
        "target"
    ],
    "applet": [
        "align",
        "alt",
        "code",
        "codebase"
    ],
    "area": [
        "alt",
        "coords",
        "download",
        "href",
        "hreflang",
        "media",
        "ping",
        "rel",
        "shape",
        "target"
    ],
    "audio": [
        "autoplay",
        "buffered",
        "controls",
        "loop",
        "preload",
        "src"
    ],
    "base": [
        "href",
        "target"
    ],
    "basefont": [
        "color"
    ],
    "bgsound": [
        "loop"
    ],
    "blockquote": [
        "cite"
    ],
    "body": [
        "bgcolor"
    ],
    "button": [
        "autofocus",
        "disabled",
        "form",
        "formaction",
        "name",
        "type",
        "value"
    ],
    "canvas": [
        "height",
        "width"
    ],
    "caption": [
        "align"
    ],
    "col": [
        "align",
        "bgcolor",
        "span"
    ],
    "colgroup": [
        "align",
        "bgcolor",
        "span"
    ],
    "command": [
        "checked",
        "disabled",
        "icon",
        "radiogroup",
        "type"
    ],
    "del": [
        "cite",
        "datetime"
    ],
    "details": [
        "open"
    ],
    "embed": [
        "height",
        "src",
        "type",
        "width"
    ],
    "fieldset": [
        "disabled",
        "form",
        "name"
    ],
    "font": [
        "color"
    ],
    "form": [
        "accept",
        "accept-charset",
        "action",
        "autocomplete",
        "enctype",
        "method",
        "name",
        "novalidate",
        "target"
    ],
    "hr": [
        "align",
        "color"
    ],
    "html": [
        "manifest"
    ],
    "iframe": [
        "align",
        "height",
        "name",
        "sandbox",
        "seamless",
        "src",
        "srcdoc",
        "width"
    ],
    "img": [
        "align",
        "alt",
        "border",
        "height",
        "ismap",
        "sizes",
        "src",
        "srcset",
        "usemap",
        "width"
    ],
    "input": [
        "accept",
        "alt",
        "autocomplete",
        "autofocus",
        "autosave",
        "checked",
        "dirname",
        "disabled",
        "form",
        "formaction",
        "height",
        "list",
        "max",
        "maxlength",
        "min",
        "multiple",
        "name",
        "pattern",
        "placeholder",
        "readonly",
        "required",
        "size",
        "src",
        "step",
        "type",
        "usemap",
        "value",
        "width"
    ],
    "ins": [
        "cite",
        "datetime"
    ],
    "keygen": [
        "autofocus",
        "challenge",
        "disabled",
        "form",
        "keytype",
        "name"
    ],
    "label": [
        "for",
        "form"
    ],
    "li": [
        "value"
    ],
    "link": [
        "href",
        "hreflang",
        "integrity",
        "media",
        "rel",
        "sizes"
    ],
    "map": [
        "name"
    ],
    "marquee": [
        "bgcolor",
        "loop"
    ],
    "menu": [
        "type"
    ],
    "meta": [
        "charset",
        "content",
        "http-equiv",
        "name"
    ],
    "meter": [
        "form",
        "high",
        "low",
        "max",
        "min",
        "optimum",
        "value"
    ],
    "object": [
        "border",
        "data",
        "form",
        "height",
        "name",
        "type",
        "usemap",
        "width"
    ],
    "ol": [
        "reversed",
        "start"
    ],
    "optgroup": [
        "disabled"
    ],
    "option": [
        "disabled",
        "selected",
        "value"
    ],
    "output": [
        "for",
        "form",
        "name"
    ],
    "param": [
        "name",
        "value"
    ],
    "progress": [
        "form",
        "max",
        "value"
    ],
    "q": [
        "cite"
    ],
    "script": [
        "async",
        "charset",
        "defer",
        "integrity",
        "language",
        "src",
        "type"
    ],
    "select": [
        "autofocus",
        "disabled",
        "form",
        "multiple",
        "name",
        "required",
        "size"
    ],
    "source": [
        "media",
        "sizes",
        "src",
        "type"
    ],
    "style": [
        "media",
        "scoped",
        "type"
    ],
    "table": [
        "align",
        "bgcolor",
        "border",
        "summary"
    ],
    "tbody": [
        "align",
        "bgcolor"
    ],
    "td": [
        "align",
        "bgcolor",
        "colspan",
        "headers",
        "rowspan"
    ],
    "textarea": [
        "autofocus",
        "cols",
        "dirname",
        "disabled",
        "form",
        "maxlength",
        "name",
        "placeholder",
        "readonly",
        "required",
        "rows",
        "wrap"
    ],
    "tfoot": [
        "align",
        "bgcolor"
    ],
    "th": [
        "align",
        "bgcolor",
        "colspan",
        "headers",
        "rowspan",
        "scope"
    ],
    "thead": [
        "align"
    ],
    "time": [
        "datetime"
    ],
    "tr": [
        "align",
        "bgcolor"
    ],
    "track": [
        "default",
        "kind",
        "label",
        "src",
        "srclang"
    ],
    "video": [
        "autoplay",
        "buffered",
        "controls",
        "height",
        "loop",
        "muted",
        "poster",
        "preload",
        "src",
        "width"
    ]
}


class Attributes(object):
    """Given a beautiful soup element this will remove any elements that aren't 
    supported for that element's tagname"""
    @property
    def supported(self):
        """Returns a set of all the attributes this element supports"""
        attrs = ATTRIBUTES.get(self.element.name, [])
        attrs.extend(ATTRIBUTES["Global attribute"])
        return set(attrs)

    def __init__(self, element):
        """create an Attributes instance

        :param element: bs4 element, the element whose attributes you want to sanitize
        """
        self.element = element

    def clean(self):
        """sanitize the element"""
        supported = self.supported
        for attr in self.element.attrs.keys():
            if attr not in supported:
                del self.element[attr]


