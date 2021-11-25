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



def prepare(doc):
    doc.sluglines = [dict(date=parse('17 August 1945'), category='past')]

def action(elem, doc):
    if isinstance(elem, pf.Span) and elem.content[0].text == 'SLUGLINE': 
        prefix = 'In' 
        date = parse(elem.attributes['date']) 
        category = elem.attributes['category']
        # sequence_start = True if elem.attributes['sequence_start'] == 'true' else False
        prev_slugline = doc.sluglines[-1]
        doc.sluglines.append(dict(date=date, category=category)) 
        
        dd = relativedelta(date, prev_slugline['date']) 
        
        if dd.months > 1: 
            if prev_slugline['category'] == 'past' and category == 'interview': 
                prefix = 'Returning to the interview in' 
            
            elif category == 'past' and prev_slugline['category'] in ('interview', 'present') : 
                prefix = 'In a flashback to'  
            return pf.Strong(pf.Str(prefix), pf.Space, pf.Str(date.strftime('%B %Y')), pf.Space)
            
        else:
            return []

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
