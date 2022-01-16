#!/home/jeremy/Python3.7Env/bin/python
# -*- coding: utf-8 -*-
#
#  script.py
#
#  Copyright 2019 Jeremy Allan <jeremy@jeremyallan.com>

from operator import itemgetter
from pathlib import Path
from document.document import Document
from document.pandoc import PandocArgs

from storage.cherrytree import CherryTree
from storage.redis import rds, RedisKey

from IPython.display import Markdown as md
from dateutil.parser import parse as date_parse
import pandas as pd
import fire
import re

CATEGORIES = ('Present', 'Past')

INDEX_FILE = 'screenplay.ctd'



def load_links(link, scene):
    return dict(incident_ref=link.href, scene_ref=scene.id) 
    

def load_screenplay():
    ct = CherryTree('screenplay.ctd')
    scene_nodes = [n for n in ct.nodes('Scenes') if n.document_link]
    mfields = ('status', 'date', 'category', 'synopsis' )
    incidents = pd.DataFrame([dict(
            incident_ref=n.id,
            incident=n.name,
            story=ct.ancestors(n)[1].name
        )
            for c in ('Present', 'Past')
            for n in ct.nodes(c)
            if n.level > 2
            if not n.name.startswith("~")])
    incidents['incident_no'] = incidents.index
    scenes = pd.DataFrame([dict(scene_ref=n.id, 
                                scene=n.name, 
                                filepath=n.document_link) 
                                for n in scene_nodes])
    scenes['scene_no'] = scenes.index
    docs = pd.DataFrame([dict(doc=Document.read_file(s.document_link)) for s in scene_nodes])
    docs['filepath'] = docs.doc.apply(lambda x: x.filepath)
    docs['content'] = docs.doc.apply(lambda x: x.content)
    for mfield in mfields:
        docs[mfield] = docs.doc.apply(lambda x: x.metadata.get(mfield, None))
    docs['date'] = docs.date.apply(lambda x: date_parse(x))
    
    docs.drop('doc', axis=1, inplace=True)
    links = pd.DataFrame([dict(incident_ref=l.href, scene_ref=s.id) for s in scene_nodes for l in s.links if l.type == 'node'])
    return incidents.merge(links, how='left', on='incident_ref')\
                        .merge(scenes, how='left', on='scene_ref')\
                        .merge(docs, how='left', on='filepath').fillna('No Data').drop_duplicates()     
                        
                        
def node_data(node):
        doc =  Document.read_file(node.document_link) 
        return dict(scene=node.name, date=date_parse(doc.metadata['date']))
    
def unlinked_scenes():
    ct = CherryTree('screenplay.ctd')
    return pd.DataFrame([node_data(n) 
                        for n in ct.nodes('Scenes') \
                        if n.document_link \
                        if not any(l for l in n.links if l.type == 'node')])

def broken_links():
    ct = CherryTree('screenplay.ctd')
    for node in [n for n in ct.nodes('Scenes') if n.document_link]: 
        for link in [l for l in node.links if l.type == 'node']:
            try:
                ct.find_node_by_id(link.href).name 
            except AttributeError:
                print('broken link at', node.name)

def story_backlinks(story_name):                
    ct = CherryTree('screenplay.ctd') 
    story_node = ct.find_node_by_name(story_name)
    for linked_node in ct.backlinked_nodes(story_node):
        yield linked_node
                     

def character_list():
nlp = spacy.load('en_core_web_md')
ruler = nlp.add_pipe("entity_ruler") 
ct = CherryTree('screenplay.ctd') 
patterns = [{'id':snake_case(n.name), 
             'label':'CHARACTER', 
             'pattern': [{'LOWER': {'REGEX': '|'.join([i.lower() for i in n.name.split()])}}]} 
            for n in ct.nodes('Characters')] 

ruler.add_patterns(patterns) 
ruler.to_disk('characters.jsonl')


class ScreenplayData():

    def __init__(self):
        global CT
        CT = CherryTree(INDEX_FILE)
        incidents = pd.DataFrame([load_incident(n)
                                  for c in CATEGORIES
                                  for n in CT.nodes(c)
                                  if n.level > 2
                                  if not n.name.startswith("~")])
        incidents['incident_no'] = incidents.index
        scenes = pd.DataFrame([load_scene(n) for n in CT.nodes('Scenes')])
        scenes['scene_no'] = scenes.index
        scenes['date'] = scenes[scenes.date.notna()].date.apply(
            lambda x: date_parse(x))
        scene_links = pd.DataFrame([load_links(l, s)
                                    for s in CT.nodes('Scenes') for l in s.links if l.type == 'node'])

        self.df = incidents.merge(scene_links, how='left', on='incident_ref')\
            .merge(scenes, how='left', on='scene_ref')

    def filter_by_keyword(self, negate=False, **kwargs):
        """returns subset filtered by sequence, category, story, scene regex patterns"""
        prefix = "~" if negate else ""
        clauses = [
            f'({prefix}{f.lower()}.str.contains("{a}"))' for f, a in kwargs.items()]
        query = ' & '.join(clauses)
        self.df = self.df.dropna(subset=kwargs).query(query)
        return self

    def filter_by_existence(self, **kwargs):
        """returns subset filtered by whether field is null or not"""
        clauses = [
            f'({f.lower()}.{"notna()" if a else "isna()"})' for f, a in kwargs.items()]
        query = ' & '.join(clauses)
        self.df = self.df.query(query)
        return self

    def date_range(self, *bounds):
        min_date = date_parse(bounds[0])
        try:
            max_date = date_parse(bounds[1])
        except IndexError:
            max_date = date_parser('1 January 1990')
        tdf = self.df.dropna(subset=['date'])
        self.df = tdf[(min_date <= tdf.date) & (tdf.date <= max_date)]
        return self

    @property
    def display_count(self):
        return self.df.count()

    @property
    def display_outline(self):
        return self.df.sort_values('scene_no')[['sequence', 'story', 'incident', 'scene', 'date', ]]

    @property
    def display_content(self):
        for r in self.df.dropna(subset=['content']).sort_values(['scene_no', 'incident_no']).itertuples():
            try:
                display(
                    md(f'**{r.scene} - {r.date.strftime("%B %Y")}** :  {r.content.lstrip()}'))
            except Exception as e:
                print(f'Cannot display {r.scene} because {e}')


def output_screenplay():
    CT = CherryTree(INDEX_FILE)
    rkey = RedisKey(namespace='omaf', component='slugline.data')

    for i, node in enumerate([n for n in CT.nodes('Scenes') if n.document_link]):
        try:
            previous_sibling_key = str(
                rkey(CT.previous_sibling(node).id))
        except AttributeError:
            previous_sibling_key = str(rkey(1100000))

        data = dict(
            previous_sibling_key=previous_sibling_key,
            parent_key=str(rkey(CT.parent(node).id)),
            level=node.level,
            name=node.name,
            id=node.id
        )
        scene_key = str(rkey(node.id))
        [rds.hset(scene_key, k, v) for k, v in data.items()]
        rds.expire(scene_key, 120)
        print(PandocArgs(input=node.document_link,
                         metadata=dict(slugline_data_key=scene_key),
                         filters=['insert_slugline.lua',
                                  'print_output_file.lua']))
        if i > 20:
            break


if __name__ == '__main__':
    fire.Fire(output_screenplay) 
    
[['story', 'incident', 'scene']]

'''
def output_treatment(self, output_file):

'''
