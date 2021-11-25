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
from storage.redis import rds, RedisKey
from utility.strings import snake_case, title_case
import dateutil
import datetime
import spacy
import pandas as pd
import fire 
import re 


CATEGORIES = ('Present', 'Past', 'Interviews', 'Writings') 

def get_document_link(node):
    document_link = next(node.links(label='Story'), None) 
    if not document_link:
        return None 
    if not Path(str(document_link)).exists():
        raise FileNotFoundError
    return str(document_link)

def build_story_df(ct):
    story_data = [] 
    for story_node in [n for n in ct.nodes() 
                       if not n.name.startswith("~") 
                       if get_document_link(n)]:
        story_doc = Document.read_file(get_document_link(story_node))
        
        try:
            datestamp = dateutil.parser.parse(story_doc.date)
        except:
            datestamp = None
            
        story_data.append(dict(
            identifier= story_node.id, 
            category=story_doc.category,
            story=story_node.parent.name,
            scene=story_node.name,
            status=story_doc.status,
            level=story_node.level,
            datestamp = datestamp,
            content=story_doc.content
        ))
    
    
    dfn = pd.DataFrame(story_data)
                              
    dfl = pd.DataFrame([dict(sequence=s.name, sequence_no=sno, identifier=l.href, story_no=lno) 
            for sno, s in enumerate(ct.nodes('Synopsis')) 
            for lno, l in enumerate(s.links(type='node'))])
    
    df = dfn.merge(dfl, how='left', on='identifier')
    df.sequence.fillna('Unplaced', inplace=True)
    df.sequence_no.fillna(0, inplace=True)
    df.story_no.fillna(0, inplace=True) 
    
    
    return df.sort_values(['sequence_no', 'story_no'])


def output_synopsis_with_pandas():
    ct = CherryTree('screenplay.ctd') 
    df = build_story_df(ct) 
    grp = df.groupby('sequence', sort = False)
    for sequence, items in grp:
        sequence_start = True
        for link in items.story_link.values:
            print(PandocArgs(input=link, 
            filters=['insert_slugline.lua', 'print_output_file.lua'],
            metadata=dict(sequence_start=sequence_start)))
            sequence_start = False 
        if sequence == 'Cameron Does His Research':
            break
        
def output_synopsis():
    ct = CherryTree('screenplay.ctd') 
    for story_node in [ct.find_node_by_id(l.href) 
        for n in ct.nodes('Synopsis') 
        for l in n.links if l.type == 'node']: 
        story_link = next((l.href for l in story_node.links if l.type == 'file' and l.label == 'Story'), None) 
        if not story_link:
            continue 
        context = story_node.parent.name
        print(PandocArgs(input=link, 
            filters=['insert_slugline.lua', 'print_output_file.lua'],
            metadata=dict(context=context)))
        
    
    
def story_placements(): 
    ct = CherryTree('screenplay.ctd')
    return build_story_df(ct) 
    
def output_stories():
    ct = CherryTree('screenplay.ctd')
    df = build_story_df(ct)
    outputpath = Path('stories')
       
    new_story = False
    for story in [s for s in df.itertuples() if s.content if not s.doc]:
        outputfile = outputpath.joinpath(snake_case(story.scene)).with_suffix('.md') 
        if outputfile.exists():
            print('Unlinked story file for', story.scene)
        try:
            date = story.datestamp.strftime('%d %B %Y')
        except:
            date = 'No Date'
        metadata = dict(title=story.scene, date=date, status='new')
        doc = Document(content=story.content, metadata=metadata, filepath=outputfile)
        # doc.write_file() 
        new_story = True
       
if __name__ == '__main__':
    fire.Fire({'place': story_placements, 
                'output': output_synopsis,
                'story':output_stories}) 
    
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
        
redis_keys = dict(
    modified = RedisKey(namespace='omaf', component='modified', identifier='nodes'),
    datestamp = RedisKey(namespace='omaf', component='datestamp'),
    sentences = RedisKey(namespace='omaf', component='sentences'),
    characters= RedisKey(namespace='omaf', component='characters')
    )

DEFAULT_DAYS = dict(early=7, mid=15, late=21) 
IDE_PAT = re.compile('(early|mid|late)') 
LINEFEED_PAT = re.compile('\n*$')


def make_datestamp(first_sent):
    for date_ent in [e for e in first_sent.ents if e.label_ in ('DATE', 'TIME')]:
        m = IDE_PAT.search(date_ent.text)
        if m:
            default_day = DEFAULT_DAYS[m.group(1)] 
        else:
            default_day = 4
        default_date = datetime.datetime(1988, 1, default_day)
        try:
            datestamp = dateutil.parser.parse(date_ent.text, fuzzy=True, default=default_date) 
        except:
            continue
        else:
            return datestamp.isoformat(' ') 
    return 'No Date'


def is_modified(node):
    timestamp = rds.hget(redis_keys['modified'].key(), node.id) 
    if not timestamp:
        return True 
    elif timestamp < node.modified:
        return True 
    else:
        return False

def store_entities(nodes):
    nlp = spacy.load('en_core_web_md')  
    ruler = nlp.add_pipe('entity_ruler', before='ner') 
    ruler.from_disk('characters/patterns.jsonl') 

        
    for doc, node in nlp.pipe([(LINEFEED_PAT.sub(n.content, ''), n) for n in nodes if n.content], as_tuples=True): 
        sents = list(doc.sents) 
        if len(sents) == 0:
            print(f'No content in {node.name}') 
            continue 
            
        rds.set(redis_keys['datestamp'].key(node.id), make_datestamp(sents[0]))
        rds.set(redis_keys['sentences'].key(node.id), len(sents)) 
    
        [rds.sadd(redis_keys['characters'].key(node.id), e.ent_id_) for e in doc.ents if e.label_ == 'CHARACTER']
    
        rds.hset(redis_keys['modified'].key(), node.id, datetime.datetime.now().timestamp()) 

    
def story_row(node):
    try:
        datestamp = datetime.datetime.fromisoformat(rds.get(redis_keys['datestamp'].key(node.id))) 
    except:
        datestamp = None 
        
    context = list(node.ancestors) 

    
   '''
