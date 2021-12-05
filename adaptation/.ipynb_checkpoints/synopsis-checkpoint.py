#!/home/jeremy/Python3.7Env/bin/python
# -*- coding: utf-8 -*-
#
#  script.py
#
#  Copyright 2019 Jeremy Allan <jeremy@jeremyallan.com> 


from pathlib import Path
from document.document import Document
from storage.cherrytree import CherryTree
from IPython.display import Markdown as md
from dateutil.parser import parse as date_parse
import pandas as pd
import fire 
import re 

def node_data(node):
    return dict( 
        identifier=node.id, 
        story = node.ancestors[1].name, 
        scene=node.name,
        notes = node.texts if len(node.texts) > 10 else None,
        content = node.content)
    
def doc_data(node):
    document_link = next(node.links(label='Story|Document'), None) 
    if not document_link:
        return False
        
    if not Path(str(document_link)).exists():
        print(f'document_link for {node.name} not valid') 
        return False
    document = Document.read_file(str(document_link))
    data = dict(
        identifier=node.id,
        document_link = str(document_link),
        text= document.content.lstrip('\n')
    )
    for key in ('title', 'category', 'status'):
        data[key] = document.metadata.get(key, None)
        
    try:
        date = date_parse(document.date) 
    except:
        date = None
    finally:
        data['date'] = date
    return data 
    
def build_df(ct):
    nodes =  [n for c in CATEGORIES for n in ct.nodes(c) 
              if n.level > 2 
              if not n.name.startswith("~")]
    
    dfn = pd.DataFrame([node_data(n) for n in nodes])

    dfd = pd.DataFrame(filter(None, [doc_data(n) for n in nodes]))
                              
    dfl = pd.DataFrame([dict(sequence=s.name, sequence_no=sno, identifier=l.href, story_no=lno) 
            for sno, s in enumerate(ct.nodes('Synopsis')) 
            for lno, l in enumerate(s.links(type='node'))])
    
    return dfn.merge(dfd, how='left', on='identifier').merge(dfl, how='left', on='identifier')


CATEGORIES = ('Present', 'Past') 

class Synopsis():
    def __init__(self, input_arg):
        if isinstance(input_arg, pd.DataFrame):
            self.df = input_arg 
        elif isinstance(input_arg, CherryTree):
            self.df = build_df(input_arg)
        elif isinstance(input_arg, str):
            self.df = build_df(CherryTree(input_arg)) 
        else:
            raise TypeError(input_arg, 'unknown')
        

    def filter_stories(self, **kwargs):
        """returns subset filtered by sequence, level, category, story, scene regex patterns"""
        clauses = dict(
            sequence='(sequence.notnull()) & (sequence.str.contains("{}"))',
            level='level == {}',
            category='(category.notnull()) & (category.str.contains("{}"))',
            story='story.str.contains("{}")',
            scene='scene.str.contains("{}")',
            text='(text.notnull()) & (text.str.contains("{}"))'
        )
        query = ' & '.join([f'({clauses[k].format(v)})' for k,v in kwargs.items() ])
        return Synopsis(self.df.dropna(subset=kwargs).query(query))

    def unmade_stories(self):
        return Synopsis(self.df[self.df.document_link.isna()])

    def unplaced_stories(self):
        return Synopsis(self.df[self.df.sequence.isna()])

    def date_range(self, *bounds):
        min_date = date_parse(bounds.pop[0]) 
        max_date = date_parse(bounds[0]) if len(bounds) > 0 else date_parser('1 January 1990') 
        query = 'min_date <= date <= max_date'
        return Synopsis(self.df.dropna(subset=['date']).query(query).groupby('sequence', sort=False).agg({'date':[min, max]}))

    
    @property
    def display_scenes(self):
        return self.df.sort_values(['sequence_no', 'story_no'])[['story', 'scene', 'date', 'sequence']]
    
    @property
    def display_text(self):
        for r in self.df.dropna(subset=['text']).sort_values(['sequence_no', 'story_no']).itertuples():
            try:
                display(md(f'**{r.scene} - {r.date.strftime("%B %Y")}** :  {r.text.lstrip()}')) 
            except Exception as e:
                print(f'Cannot display {r.scene} because {e}')


    
'''
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
    
    
def output_synopsis(index_file):
    ct = CherryTree(index_file) 
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
        
    
    
def story_placements(index_file): 
    ct = CherryTree(index_file)
    return build_story_df(ct) 
    

       
if __name__ == '__main__':
    fire.Fire({'place': story_placements, 
               'output': output_synopsis}) 

    
'''
