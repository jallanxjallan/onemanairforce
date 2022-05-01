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
import json

@define
class Slugline():
    date = field(converter=parse_date)
    location = field(default=None)
    category = field(default=None)
    xdate = field(default=None)
    prefix= field(default='')
    date_string = field(default='')
    location_string = field(default='')

    def set_date(self, ps):
        self.date_string = self.date.strftime("%B %Y")
        if self.xdate:
            self.prefix = 'On'
            self.date_string = self.date.strftime("%d %B %Y")
        else:
            dd = relativedelta(self.date, ps.date)
            if dd.years < -10 and ps.category in ('interview', 'research'):
                self.prefix = 'Flashing back to'
            elif dd.years > 10 and self.category in ('interview', 'research'):
                self.prefix = 'Returning to'
            elif dd.days > 10:
                self.prefix = 'Later in'
            else:
                self.date_string = ''

    def set_location(self, ps, doc):
        try:
            self.location_string = doc.locations[self.location]['display'] if self.location != ps.location else ''
        except KeyError:
            self.location_string = 'No location match'

    def output_slugline(self):
        slugline = f'{self.prefix} {self.date_string} {self.location_string}'
        return pf.Strong(pf.Str(slugline.lstrip()), pf.Space)

def prepare(doc):
    doc.sluglines = [Slugline(date='17 August 1945', location='Jakarta')]
    with open('locations.json') as fp:
        doc.locations = json.load(fp)

def action(elem, doc):

    if isinstance(elem, pf.Span) and elem.content[0].text == 'SLUGLINE':
        cs = Slugline(**elem.attributes)
        ps = doc.sluglines[-1]
        cs.set_date(ps)
        cs.set_location(ps, doc)
        doc.sluglines.append(cs)
        return cs.output_slugline()


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
                         doc=doc)

if __name__ == '__main__':
    main()
