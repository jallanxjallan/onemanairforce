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
import json
from pathlib import Path

with open('locations.json') as infile:
    location_map = {i['location']:i['display'] for i in json.load(infile)}

@attr.s
class SluglineData():
    date =  attr.ib(converter=lambda x: parse(x))    
    location = attr.ib(converter=lambda x: location_map.get(x, x))
    wrap_scene = attr.ib(default=False) 



def format_slugline(sl, psl):

    dsp_date = sl.date.strftime('%d %B %Y')

    
    if not psl: 
        date = dsp_date
        location = sl.location 
    
    else:
    
        location = sl.location if sl.location != psl.location else '' 
        dd = relativedelta(sl.date, psl.date)
        
        if sl.date == psl.date:
            date='Later that day'
            
        elif dd.years < -2:
             date = f'Flashing back to {dsp_date}' 

        elif dd.days == 1:
             date = 'The following day'

        elif 1 < dd.days < 5:
             date ='A few days later'
            
        elif dd.years > 2:
            
            if sl.wrap_scene == 'Interviews':
                date = 'Returning to the interview on {dsp_date}' 
            elif sl.wrap_scene == 'Writings':
                date = 'Returning to {dsp_date}' 
            else:
                date = dsp_date
        else:
            date = dsp_date
        
    
    return f'{date} at {location}'

def prepare(doc):
    doc.sluglines = []

def action(elem, doc):
    if isinstance(elem, pf.Span) and 'date' in elem.attributes:
        try:
            sluglinedata = SluglineData(**elem.attributes)
        except Exception as e:
            pf.debug(e)
            return elem 
        try:
            prev_sluglinedata = doc.sluglines[-1] 
        except IndexError:
            prev_sluglinedata = None
             
        slugline = format_slugline(sluglinedata, prev_sluglinedata)
        if slugline:
            elem = pf.Span(pf.Strong(pf.Str(slugline), pf.Space))
        else:
            elem = []
        doc.sluglines.append(sluglinedata)
    return elem


def main(doc=None):
    return pf.run_filter(action,
                         prepare=prepare,
                         doc=doc)

if __name__ == '__main__':
    main()
