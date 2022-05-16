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
    date = field(converter=parse_date)
    location = field()
    name = field()

    def slugline(self, ps, doc):
        dd = relativedelta(self.date, ps.date)
        date = None
        location = None
        if dd.months > 0 or abs(dd.years) > 0:
            date = f'In {self.date.strftime("%B %Y")}'

        location_node = doc.ct.find_node_by_name(self.location)
        if not location_node:
            pf.debug(f'No location for {self.name}')
        elif not self.location == ps.location:
            location = location_node.name
            
        if date and location:
            return f'{date} {location}'
        elif date:
            return date
        elif location:
            return location
        else:
            return 'Slugline Error'


def uppercase_name(elem, doc):
    if isinstance(elem, pf.Str):
        word = elem.text
        if word in doc.character_names and doc.character_names[word] == 0:
            elem.text = word.upper()
            doc.character_names[word] = 1
    return elem


def prepare(doc):
    doc.sluglines = [Slugline(name='Placeholder', date='17 August 1945', location='Jakarta')]
    doc.ct = CherryTree('screenplay.ctd')

def action(elem, doc):
    if isinstance(elem, pf.Span) and elem.content[0].text == 'SLUGLINE':
        try:
            cs = Slugline(**{k:v for k,v in elem.attributes.items() if k in ['name', 'date', 'location']})
        except Exception as e:
            pf.debug(f'{e} with {elem.attributes}')
            return pf.Strong(pf.Str('Slugline Error'))
        ps = doc.sluglines[-1]
        doc.sluglines.append(cs)
        return pf.Strong(pf.Str(cs.slugline(ps, doc)), pf.Space)

def finalize(doc):
    doc.character_names = {w.strip():0 for c in doc.ct.nodes('Characters') for w in c.name.split()}
    uppercased = doc.walk(uppercase_name)
    return uppercased


def main(doc=None):
    return pf.run_filter(action,
                         prepare=prepare,
                         finalize=finalize,
                         doc=doc)

if __name__ == '__main__':
    main()
