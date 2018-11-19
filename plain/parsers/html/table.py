# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import
from collections import defaultdict

from ..base import Base



class Headers(object):
    def __init__(self):
        self.headers = defaultdict(dict)
        self.colgroups = defaultdict(list)
        self.keys = defaultdict(dict)

    def add_colgroup(self, offset, span, text):
        for i in range(offset, offset + span):
            self.colgroups[i].append(text)

    def set_key(self, name, index, text):
        if not text:
            text = str(index)
        self.keys[name][index] = text

    def set_header(self, name, offset, span, text):
        for i in range(offset, offset + span):
            self.headers[name][i] = text

    def get_key(self, index):
        ret = str(index)
        for name in self.keys.keys():
            if index in self.keys[name]:
                ret = self.keys[name][index]
                break
        return ret

    def get_headers(self, index):
        ret = []
        for name in self.headers.keys():
            ret.append(self.headers[name][index])
        return ret


class Table(Base):
    """
    https://developer.mozilla.org/en-US/docs/Web/HTML/Element/table
    """

    @property
    def tables(self):
        return self.fields["tables"]

    @property
    def dls(self):
        return self.fields["dls"]

    def _simplify(self):
        # http://stackoverflow.com/questions/11790535/extracting-data-from-html-table
        datasets = {"tables": [], "dls": []}
        soup = self.soup
        datasets["tables"] = self.find_tables(soup)
        datasets["dls"] = self.find_dls(soup)
        return datasets

    def is_header_row(self, tr, headers):
        ret = False

        all_scope_col = True
        has_th = False
        has_td = False
        has_keys = len(headers.keys) > 0

        for col in tr.find_all(["td", "th"], recursive=False):
            if col.name == "th":
                has_th = True
                scope = col.get("scope", "col")
                if scope != "col":
                    all_scope_col = False

            elif col.name == "td":
                has_td = True


        if has_td:
            # if we already have keys, then assume this is a content row if it
            # fails any of the above
            if not has_keys:
                ret = all_scope_col and has_th

        else:
            ret = True



        return ret

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

    def find_table(self, table):
        d = {
            "caption": "",
            "rows": [],
        }
        headers = Headers()

        for c in table.children:
            if c.name == "caption":
                d["caption"] = c.get_text(strip=True)

            elif c.name == "colgroup":
                # https://developer.mozilla.org/en-US/docs/Web/HTML/Element/colgroup
                self.find_colgroup(c, headers)

            elif c.name == "thead":
                # https://developer.mozilla.org/en-US/docs/Web/HTML/Element/thead
                for tr in c.find_all("tr", recursive=False):
                    self.find_headers(tr, headers)

        d["rows"] = self.find_content(table, headers)
        return d

        #pout.v(headers, d)

    def find_content(self, table, headers):
        rows = []
        cols_x, rows_y = self.find_dimensions(table)

        tbody = table.find("tbody", recursive=False)
        if not tbody: tbody = table
        elems = [tbody]

        # https://developer.mozilla.org/en-US/docs/Web/HTML/Element/tfoot
        tfoot = table.find("tfoot", recursive=False)
        if tfoot:
            elems.append(tfoot)

        for elem in elems:
            for tr in elem.find_all("tr", recursive=False):
                if self.is_header_row(tr, headers):
                    self.find_headers(tr, headers)

                else:
                    row = []
                    for col in tr.find_all(["td", "th"], recursive=False):
                        text = col.get_text().strip()
                        if not text:
                            img_urls = []
                            for img in col.find_all("img"):
                                img_urls.append(img.get("src"))
                            text = "\n".join(img_urls)

                        row.append(text)
                        colspan = int(col.get("colspan", 1))
                        if colspan > 1:
                            row.extend([None] * colspan)

                        # TODO: We don't take rowpsan into account at all

                    if len(row) < cols_x:
                        row.extend([None] * (cols_x - len(row)))

                    d = {}
                    for i, v in enumerate(row):
                        k = headers.get_key(i)
                        hs = headers.get_headers(i)
                        d[k] = {
                            "headers": hs,
                            "value": v
                        }
                    rows.append(d)

        return rows


    def find_headers(self, tr, headers):
        """
        https://developer.mozilla.org/en-US/docs/Web/HTML/Element/th
        """
        offset = 0
        for th in tr.find_all(["th", "td"], recursive=False):
            name = " ".join(th.get("class", []))
            span = int(th.get("colspan", 1))
            text = th.get_text(strip=True)
            if span == 1:
                # if the th is for one column then it is a key
                headers.set_key(name, offset, text)

            else:
                headers.set_header(name, offset, span, text)

            offset += span


    def find_colgroup(self, colgroup, headers):
        """
        https://developer.mozilla.org/en-US/docs/Web/HTML/Element/colgroup
        """
        offset = 0

        # if the <colgroup> itself has a span then there won't be any <col> tags
        span = int(colgroup.get("span", 0))
        if span:
            text = c.get("class", "")
            if text:
                headers.add_colgroup(offset, span, text)

        else:
            for c in colgroup.find_all("col", recursive=False):
                span = int(c.get("span", 1))
                text = c.get("class", "")
                if text:
                    headers.add_colgroup(offset, span, text)

                offset += span

        return headers

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



class Table2(Base):
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





