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
from dateutil.parser import parse
import attr

@attr.s
class Slugline():
    date =  attr.ib()
    location = attr.ib()
    prev_date =  attr.ib(default=None)
    prev_location = attr.ib(default=None)
    sequence_start = attr.ib(default=False, converter=lambda x: True if x == 'true' else False)

    def __attr_post_init__(self):
        if prev_date:
            self.dd = relativedelta(parse(self.date), parse(self.prev_date))
            self.dl = self.location == self.prev_location


    def __str__(self):
        return self._format_slugline()

    def _format_slugline(self):
        if self.sequence_start:
            return f'{self.date} {self.location}'
        else:
            return 'continuing sequence'



        if dd.years > 30:
            slugline = Slugline(prefix ='Returning to modern-day interview')

        elif dd.years < -30:
            slugline = Slugline(prefix='In a flashback to', date=date)

        elif dd.days == 1:
            slugline = Slugline(prefix='The following day')

        elif 1 < dd.days < 5:
            slugline = Slugline(prefix='A few days later')

        else:
            slugline = Slugline()

    if dl:
        slugline.location = loc

    return str(slugline)

def prepare(doc):
    doc.sluglines = []

def action(elem, doc):
    if isinstance(elem, pf.Span) and 'date' in elem.attributes:
        args=elem.attributes
        doc.sluglines.append(args)
        slugline = Slugline(**args)
        if args['sequence_start'] == 'false':
            prev_meta = doc.sluglines[-2]
            slugline.prev_date = prev_meta['date']
            slugline.prev_location = prev_meta['location']
        pf.debug(slugline)



def main(doc=None):
    return pf.run_filter(action,
                         prepare=prepare,
                         doc=doc)

if __name__ == '__main__':
    main()
