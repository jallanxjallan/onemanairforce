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
import redis

def prepare(doc):
    doc.current_timestamp = datetime.datetime.now()
    doc.r = redis.Redis(decode_responses=True)

def action(elem, doc):
    if isinstance(elem, pf.Header) and elem.level == 9:
        key = pf.stringify(elem)
        date = doc.r.hget(key, 'date')
        title = doc.r.hget(key, 'title')
        if not date:
            pf.debug('no date found for ', title)
            return elem
        header = pf.Str(f'{dateparser.parse(date).strftime("%B %Y")} : {title}')
        return pf.Header(header, level=1)
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
