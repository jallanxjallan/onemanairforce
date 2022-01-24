#!/home/jeremy/Python3.7Env/bin/python
# -*- coding: utf-8 -*-
#
#  script.py
#
#  Copyright 2019 Jeremy Allan <jeremy@jeremyallan.com>

from document.document import Document
from pathlib import Path

from storage.cherrytree import CherryTree

from IPython.display import Markdown as md
from dateutil.parser import parse as date_parse
import pandas as pd
import re
import fire


DOC_FIELDS = ('status', 'date', 'category', 'synopsis', 'include' )

CT = CherryTree('screenplay.ctd') 

DOCUMENTS = Path('scenes')

SCENES = [n for n in CT.nodes('Scenes') if n.document_link]

STORY_NODE = 'Stories'


def link_data((link, scene):
    return dict(incident_ref=link.href, scene_ref=scene.id)) 

def incident_data(node):
    return dict(incident_ref=node.id,
                incident=node.name,
                story=CT.ancestors(node)[1].name
            )

def scene_data(node):
    return dict(scene_ref=node.id,
                scene=node.name,
                filepath=node.document_link)


class Screenplay():
    def __init__(self):
        self.df = self.load_screenplay()

    def load_screenplay(self):

        incidents = pd.DataFrame([incident_data(n) for n in CT.nodes(STORY_NODE) if n.level > 2])
        incidents['incident_no'] = incidents.index
        scenes = pd.DataFrame([scene_data(n) for n in SCENES])
        scenes['scene_no'] = scenes.index
        docs = pd.DataFrame([dict(doc=Document.read_file(s.document_link)) for s in SCENES])
        docs['filepath'] = docs.doc.apply(lambda x: x.filepath)
        docs['content'] = docs.doc.apply(lambda x: x.content)
        for mfield in DOC_FIELDS:
            docs[mfield] = docs.doc.apply(lambda x: x.metadata.get(mfield, None))
        docs['date'] = docs.date.apply(lambda x: date_parse(x))
        docs['date_string'] = docs.date.apply(lambda x: x.strftime('%B %Y'))

        docs.drop('doc', axis=1, inplace=True)
        links = pd.DataFrame([dict(incident_ref=l.href, scene_ref=s.id) 
                              for s in SCENES 
                              for l in s.links if l.type == 'node'])
        
        return incidents.merge(links, how='left', on='incident_ref')\
                        .merge(scenes, how='left', on='scene_ref')\
                        .merge(docs, how='left', on='filepath')\
                        .fillna('No Data').drop_duplicates()

    def search(self, **kw):
        querys = [f'({k}.str.contains("{v}", case=False))' for k,v in kw.items()]
        return self.df.query(' & '.join(querys))[['story', 'incident', 'scene', 'date_string']]

    def unplaced_incidents(self):
        return self.df[self.df.scene == 'No Data'][['story', 'incident']]


    def unlinked_scenes(self):
        def scene_node_data(scene_node):
                doc =  Document.read_file(scene_node.document_link)
                return dict(scene=scene_node.name, date=date_parse(doc.metadata['date']))

        return pd.DataFrame([scene_node_data(n)
                            for n in SCENES 
                            if not any(l for l in n.links if l.type == 'node')])

    def broken_links(self):
        for node in SCENES:
            for link in [l for l in node.links if l.type == 'node']:
                try:
                        CT.find_node_by_id(link.href).name
                except AttributeError:
                    yield 'broken link at', node.name 
                    
    def orphan_documents(self):
        return set(str(f) 
                   for f in DOCUMENTS.iterdir())\
                    .difference(set(n.document_link for n in SCENES))

if __name__ == '__main__':
    fire.Fire(Screenplay)



'''def character_list():
    nlp = spacy.load('en_core_web_md')
    ruler = nlp.add_pipe("entity_ruler")
    ct = CherryTree(INDEX_FILE)
    patterns = [{'id':snake_case(n.name),
                 'label':'CHARACTER',
                 'pattern': [{'LOWER': {'REGEX': '|'.join([i.lower() for i in n.name.split()])}}]}
                for n in ct.nodes('Characters')]

    ruler.add_patterns(patterns)
    ruler.to_disk('characters.jsonl')

    def display_content(df):
        for r in df.dropna(subset=['content']).sort_values(['scene_no', 'incident_no']).itertuples():
            try:
                display(
                    md(f'**{r.scene} - {r.date.strftime("%B %Y")}** :  {r.content.lstrip()}'))
            except Exception as e:
                print(f'Cannot display {r.scene} because {e}')
'''
