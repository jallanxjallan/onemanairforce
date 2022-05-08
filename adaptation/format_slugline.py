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
from storage.cherrytree import CherryTree

@define
class Slugline():
    date = date = field(converter=parse_date)
    location = field()
    category = field(default=None)
    xdate = field(default=None)

    def date_string(self, ps):
        return self.date.strftime("%B %Y")


        # if not self.date:
        #     self.date_string = "No date found"
        # return
        #
        # self.date_string = self.date.strftime("%B %Y")
        # if self.xdate:
        #     self.prefix = 'On'
        #     self.date_string = self.date.strftime("%d %B %Y")
        # else:
        #     dd = relativedelta(self.date, ps.date)
        #     if self.date.year != 1988 and ps.category in ('interview', 'research'):
        #         self.prefix = 'Flashing back to'
        #     elif self.date.year == 1988 and self.category in ('interview', 'research'):
        #         self.prefix = 'Returning to'
        #     elif dd.days > 10:
        #         self.prefix = 'Later in'
        #     else:
        #         self.date_string = ''


    def location_string(self, ps, doc):
        return self.location
        # location_node = doc.ct.find_node_by_name(self.location)
        # if not location_node:
        #     self.location_string = 'No location found'
        # else:
        #     location_data = next(location_node.codeboxes(), None)
        #     if not location_data:
        #         self.location_string = 'No location display found'
        #     else:
        #         self.location_string = location_data['display']

def prepare(doc):
    doc.sluglines = [Slugline(date='17 August 1945', location='Jakarta')]
    doc.ct = CherryTree('screenplay.ctd')

def action(elem, doc):
    if isinstance(elem, pf.Span) and elem.content[0].text == 'SLUGLINE':
        try:
            cs = Slugline(**elem.attributes)
        except Exception as e:
            pf.debug(f'{e} with {elem.attributes}')
            return pf.Strong(pf.Str('Slugline Error'))
        ps = doc.sluglines[-1]
        doc.sluglines.append(cs)
        return pf.Strong(pf.Str(f'{cs.date_string(ps)}  {cs.location_string(ps,doc)}'), pf.Space)


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
