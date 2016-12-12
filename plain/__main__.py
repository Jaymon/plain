# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import

import captain
from captain.decorators import arg

from plain import Table


@arg("url", help="the url of the html table you want")
#@arg("--csv", action="store_true", help="")
@arg("--json", action="store_true", help="print table data to the screen as json")
def main_table(url, json):

    t = Table(url)





if __name__ == "__main__":
    captain.exit()

