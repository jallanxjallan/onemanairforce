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
from dateutil.parser import parse as date_parse
import attr
import json
from pathlib import Path
from storage.redis import rds



def prepare(doc):
    doc.sluglines = {}

def action(elem, doc):
    if isinstance(elem, pf.Span) and elem.content[0].text == 'SLUGLINE': 
        sd = rds.hgetall(elem.attributes['slugline_data_key']) 
        ssd = rds.hgetall(sd['previous_sibling_key'])
        psd = rds.hgetall(sd['parent_key'])
       
        prefix = 'In' 
        date = date_parse(sd['date']) 
        
        if ssd:
            dd = relativedelta(date_parse(ssd['date']), date) 
            deltas = f'days: {dd.days} months {dd.months} years {dd.years}'
            return pf.Strong(pf.Str(date.strftime('%d %B %Y')), 
                pf.Space, pf.Str(deltas)) 
        else:
            return pf.Strong(pf.Str(prefix), pf.Space, pf.Str(date.strftime('%B %Y')), pf.Space)

    return elem


def main(doc=None):
    return pf.run_filter(action,
                         prepare=prepare,
                         doc=doc)

if __name__ == '__main__':
    main() 
    
    
'''

@attr.s
class Slugline():
    date =  attr.ib(converter=lambda x: parse(x))    
    location = attr.ib() # converter=lambda x: location_map.get(x, x))
    wrap_scene = attr.ib(default=False) 
    
    def disp_date(self):
        return self.date.strftime('%d %B %Y')
        
    def disp_loc(self):
        return location_map.get(self.location, self.location)  
        
        
def format_content(i, df): 
    if i == 0 or df.iloc[i].sequence != df.iloc[i-1].sequence:
        return format_date
    else:
        return relative_date(df.iloc[i])')



def format_date(sl, psl):
    date = None 
    location = None
    

    if not psl: 
        date = f'On {sl.disp_date()}'
        location = sl.disp_loc()
    
    else:
        location = f' at {sl.disp_loc()}' if sl.location != psl.location else None
       
        dd = relativedelta(sl.date, psl.date) 
        
        if sl.wrap_scene and sl.wrap_scene == 'interview':
            date = f'Returning to {sl.disp_date()}' 
        
        elif sl.date == psl.date:
            date = 'Later that day'
            
        elif dd.years < -2:
             date = f'Flashing back to {sl.disp_date()}' 

        elif dd.days == 1:
             date = 'The following day '

        elif 1 < dd.days < 5:
             date ='A few days later' 
             
        else:
            date = f'On {sl.disp_date()}'
            
            
    
    return f'{date} {location or ""}'
try:
            slugline = Slugline(**elem.attributes)
        except Exception as e:
            pf.debug(e)
            return elem 
        try:
            prev_slugline = doc.sluglines[-1] 
        except IndexError:
            prev_slugline = None
             
        output = format_slugline(slugline, prev_slugline)
        if output:
            elem = pf.Span(pf.Strong(pf.Str(output), pf.Space))
        else:
            elem = []
        doc.sluglines.append(slugline) 
        
'''
