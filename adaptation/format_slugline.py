#!/home/jeremy/Python3.7Env/bin/python
# -*- coding: utf-8 -*-
#
#  script.py
#
#  Copyright 2019 Jeremy Allan <jeremy@jeremyallan.com>

"""
Pandoc filter using panflute
"""

import panflute as pf
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse as parse_date
import attr


@attr.s
class Slugline():
    scene = attr.ib(default=None)
    date = attr.ib(default=None, converter=attr.converters.optional(parse_date))
    location = attr.ib(default=None)


def format_slugline(prefix, date):
    ss = [pf.Str(prefix)]
    if date:
       ss.extend([pf.Space, pf.Str(date.strftime('%B %Y'))])

    return pf.Span(pf.Strong(*ss), pf.Space)


def make_slugline(doc):
    cs = doc.sluglines[-1]
    pf.debug(cs)
    try:
        ps = doc.sluglines[-2]
    except IndexError:
        return format_slugline('In', cs.date)


    dd = relativedelta(cs.date, ps.date)

    if dd.day == 0:
        return format_slugline('Later that day', None)

    elif 1 < dd.days < 5:
        return format_slugline('A few days later', None)

    elif dd.years < -10:
        return format_slugline('Flashing back to', cs.date)

    elif dd.years > 10:
        return format_slugline('Returning to', cs.date)

    else:
        return format_slugline('In', cs.date)


def prepare(doc):
    doc.sluglines = []

def action(elem, doc):

    if isinstance(elem, pf.Span) and elem.content[0].text == 'SLUGLINE':
        doc.sluglines.append(Slugline(**elem.attributes))
        return make_slugline(doc)
    else:
        return elem


def main(doc=None):
    return pf.run_filter(action,
                         prepare=prepare,
                         doc=doc)

if __name__ == '__main__':
    main()
