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
import logging

@define
class Slugline():
    date = field(converter=parse_date)
    location = field()
    name = field()

    def format_location(self, ps, doc):
        if self.location == ps.location:
            return None
        try:
            location = doc.locations[self.location]
        except KeyError:
            logging.warning(f'Slugline Error in {self.name} ! {self.location} Invalid')
            return 'Invalid location'

        return location['display']

    def format_date(self, ps):
        try:
            date = self.date.strftime("%B %Y")
        except Exception as e:
            logging.warning(f'Slugline Error {e} in {self.name} ! {self.date} Invalid')
            return f'Slugline Error in {self.name} ! Invalid date'

        dd = relativedelta(self.date, ps.date)

        if dd.years == 0 and dd.months == 0:
            if dd.days == 0:
                date = None
            elif dd.days == 1:
                date = 'The following day'
            elif dd.days < 7:
                date = 'A few days later'
            else:
                date = f'Later in {date}'
        else:
            date = f'In {date}'
        return date

def uppercase_name(elem, doc):
    if isinstance(elem, pf.Str):
        word = elem.text
        if word in doc.characters and doc.characters[word] == 0:
            elem.text = word.upper()
            doc.characters[word] = 1
    return elem

def prepare(doc):
    ct = CherryTree('screenplay.ctd')
    doc.sluglines = [Slugline(name='Placeholder', date='17 August 1945', location='Jakarta')]
    doc.characters = {w.strip():0 for c in ct.nodes('Characters') for w in c.name.split()}
    doc.locations =  {n.name:n.data for n in ct.nodes('Locations')}

def action(elem, doc):
    if isinstance(elem, pf.Span) and elem.content[0].text == 'SLUGLINE':
        try:
            cs = Slugline(**{k:v for k,v in elem.attributes.items() if k in ['name', 'date', 'location']})
        except Exception as e:
            pf.debug(f'{e} with {elem.attributes}')
            return pf.Strong(pf.Str('Slugline Error'))
        ps = doc.sluglines[-1]
        doc.sluglines.append(cs)
        slugline = ' '.join([s for s in (cs.format_date(ps), cs.format_location(ps,doc)) if s])
        try:
            slugline = slugline[0].upper() + slugline[1:]
        except IndexError as e:
            logging.warning(f'Slugline formatting Error {e} in {cs.name}')
            slugline = 'Slugline formatting error'
        return pf.Strong(pf.Str(slugline), pf.Space)

def finalize(doc):

    uppercased = doc.walk(uppercase_name)
    return uppercased


def main(doc=None):
    return pf.run_filter(action,
                         prepare=prepare,
                         finalize=finalize,
                         doc=doc)

if __name__ == '__main__':
    main()
