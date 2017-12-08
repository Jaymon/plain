# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import

import captain
from captain.decorators import arg

from plain import Table


@arg("url", help="the url of the html table you want")
#@arg("--csv", action="store_true", help="")
#@arg("--json", action="store_true", help="print table data to the screen as json")
# TODO -- add --format that can take "json" or "csv" and defaults to "json"
def main_table(url):

    t = Table(url)
    t.parse()
    print(t.json())





if __name__ == "__main__":
    captain.exit()

