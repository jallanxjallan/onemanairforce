#!/home/jeremy/Python3.7Env/bin/python
# -*- coding: utf-8 -*-
#
#  script.py
#
#  Copyright 2019 Jeremy Allan <jeremy@jeremyallan.com> 


from collections import defaultdict
from document.document import Document
from document.pandoc import PandocArgs
from pathlib import Path
from storage.cherrytree import CherryTree
from utility.strings import snake_case
import dateutil
import datetime
import spacy
import pandas as pd
import fire 
import re 
# from format_slugline import format_slugline

DEFAULT_PRESENT_DATE=datetime.date(1988, 1, 4)
DEFAULT_PAST_DATE=datetime.date(1948, 1, 4)
nlp = spacy.load('en_core_web_md')  
ide_pat = re.compile('(early|mid|late)') 

default_days = dict(early=7, mid=15, late=21) 

    
def story_row(d):
    doc, node = d 
    data = {} 
    default_day = 4
    default_year = 1988
    datestamp = None
    story = next((a.name for a in node.ancestors if a.level == 2), None) 

    first_sent = next(doc.sents) 
    
    
    for date_ent in [e for e in first_sent.ents if e.label_ in ('DATE', 'TIME')]:
        m = ide_pat.search(date_ent.text)
        if m:
            default_day = default_days[m.group(1)] 
        default_date = datetime.datetime(1988, 1, default_day)
        try:
            datestamp = dateutil.parser.parse(date_ent.text, fuzzy=True, default=default_date) 
        except:
            continue
        else:
            break 
   
    
    return dict(
        identifier= node.id, 
        parent=node.parent.id,
        story=story,
        scene=node.name,
        content=node.content,
        level=node.level,
        datestamp=datestamp,
        doc=doc,
        node=node
    )


def place_stories():

    ct = CherryTree('screenplay.ctd') 
    story_nodes = ('Present', 'Past')
    
    docs = nlp.pipe([(n.content or 'No Content', n) for s in story_nodes for n in ct.nodes(s) if n.level > 2 ], as_tuples=True) 
    
        
    dfn = pd.DataFrame([story_row(i) for i in docs if i])
                              
    dfl = pd.DataFrame([dict(sequence=s.name, sequence_no=sno, identifier=l.href, story_no=lno) 
            for sno, s in enumerate(ct.nodes('Synopsis')) 
            for lno, l in enumerate(s.links) if l.type == 'node'])
    
    df = dfn.merge(dfl, how='left', on='identifier')
    df.sequence.fillna('Unplaced', inplace=True)
    df.sequence_no.fillna(0, inplace=True)
    df.story_no.fillna(0, inplace=True) 
    
    return df


def output_synopsis(outputfolder):
    outputpath = Path(outputfolder)
    dft = place_stories()
    df = dft.query('(sequence != "Unplaced") & (content.notna())').sort_values(['sequence_no', 'story_no']).reindex() 
    
    grp = df.groupby('sequence').agg({'content':'\n\n'.join, 'node':'first'})
    
    for g in grp.itertuples():
        outputfile = outputpath.joinpath(snake_case(g.Index)).with_suffix('.md') 
        if outputfile.exists():
            continue
        print(PandocArgs(input=g.content, 
                        output=outputfile, 
                        template='synopsis', 
                        metadata=dict(title=g.Index)))
        
    
def output_placements(): 
    df = place_stories() 
    print(df[['scene', 'datestamp']] .head(30))
    


if __name__ == '__main__':
    fire.Fire({'place': output_placements, 
                'output': output_synopsis}) 
    
'''

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
def format_slugline(row, df): 
    for doc in docs:
    first_sent = next(doc.sents) 
    for ent in first_sent.ents:
        print(ent.label_, ent.text)
    return 'Date'
 
for label in ('LOCATION', 'CHARACTER'): 
        data[inflect.plural(label.lower()] = [e.text for e in doc.ents if e.label_ == label] 
    
   '''
