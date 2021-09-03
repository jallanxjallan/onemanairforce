#!/home/jeremy/Python3.6Env/bin/python
# -*- coding: utf-8 -*-
#
#  script.py
#
#  Copyright 2019 Jeremy Allan <jeremy@jeremyallan.com>

"""
Pandoc filter using panflute
"""

import panflute as pf
import dateparser
import datetime


def prepare(doc):
    doc.current_timestamp = datetime.datetime(year=1900)

def action(elem, doc):
    if isinstance(elem, pf.Span) and 'slugline' in elem.attributes:
        date = dateparser.parse(pf.stringify(elem))
        if date is different:
            elem = pf.Para(elem)
            doc.current_timestamp = date 
        else:
            elem = {}
    return elem

def main(doc=None):
    return pf.run_filter(action,
                         prepare=prepare,
                         doc=doc)


if __name__ == '__main__':
    main()

'''
if not self.cd:
        d = date
        p = 'In'
    elif self.cd.year == 1988 and date.year < 1988:
        p = 'In a flashback to'
        d = date
    elif self.cd.year < 1988 and date.year == 1988:
        p = 'Returning to'
        d = date
    else:
        d = None
    self.cd = date
'''
