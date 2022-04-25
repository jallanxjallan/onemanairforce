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
from attr import define, field
from attr.converters import optional


@define
class Slugline():
    name = field(default=None)
    date = field(default=None, converter=optional(parse_date))
    location = field(default=None)
    category = field(default=None)
    xdate = field(default=False)

    def format_slugline(self, prefix=None):
        if self.xdate:
            date_string = f'On {self.date.strftime("%d %B %Y")}'
        else:
            date_string = f'{prefix} {self.date.strftime("%B %Y")}'
        return pf.Strong(pf.Str(date_string), pf.Space)


def format_slugline(elem, doc):
    cs = doc.sluglines[-1]
    if cs.xdate:
        return cs.format_slugline()

    try:
        ps = doc.sluglines[-2]
    except IndexError:
        return cs.format_slugline()


    dd = relativedelta(cs.date, ps.date)


    if dd.years < -10 and ps.category in ('interview', 'research'):
        return cs.format_slugline('Flashing back to')

    elif dd.years > 10 and cs.category in ('interview', 'research'):
        return cs.format_slugline('Returning to')

    elif dd.years > 10 and not cs.category in ('interview', 'research'):
        return cs.format_slugline()

    elif dd.days > 10:
        return cs.format_slugline('Later in')


    else:
        return []



def prepare(doc):
    doc.sluglines = []

def action(elem, doc):

    if isinstance(elem, pf.Span) and elem.content[0].text == 'SLUGLINE':
        doc.sluglines.append(Slugline(**elem.attributes))
        return format_slugline(elem, doc) or []


def finalize(doc):
    output_blocks = [pf.Para(pf.Str('Placeholder'))]
    for block in doc.content:
        if isinstance(block.content[0], pf.Span):
            pf.debug('Processing Span')
            output_blocks.append(block)
        else:
            output_blocks[-1].content.extend([b for b in block.content])
    return output_blocks



def main(doc=None):
    return pf.run_filter(action,
                         prepare=prepare,
                         finalize=finalize,
                         doc=doc)

if __name__ == '__main__':
    main()
