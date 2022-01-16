#!/home/jeremy/Python3.7Env/bin/python
# -*- coding: utf-8 -*-
#
#  script.py
#
#  Copyright 2019 Jeremy Allan <jeremy@jeremyallan.com>

from document.document import Document

from storage.cherrytree import CherryTree

from IPython.display import Markdown as md
from dateutil.parser import parse as date_parse
import pandas as pd
import re
import fire


CATEGORIES = ('Present', 'Past')

DOC_FIELDS = ('status', 'date', 'category', 'synopsis', 'include' )

INDEX_FILE = 'screenplay.ctd'


class Screenplay():
    def __init__(self):
        self.ct = CherryTree(INDEX_FILE) 
        self.df = self.load_screenplay()
    
    def load_links(link, scene):
        return dict(incident_ref=link.href, scene_ref=scene.id)


    def load_screenplay(self):
        
        scene_nodes = [n for n in self.ct.nodes('Scenes') if n.document_link]

        incidents = pd.DataFrame([dict(
                incident_ref=n.id,
                incident=n.name,
                story=self.ct.ancestors(n)[1].name
            )
                for c in CATEGORIES
                for n in self.ct.nodes(c)
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
        for mfield in DOC_FIELDS:
            docs[mfield] = docs.doc.apply(lambda x: x.metadata.get(mfield, None))
        docs['date'] = docs.date.apply(lambda x: date_parse(x)) 
        docs['date_string'] = docs.date.apply(lambda x: x.strftime('%B %Y'))

        docs.drop('doc', axis=1, inplace=True)
        links = pd.DataFrame([dict(incident_ref=l.href, scene_ref=s.id) for s in scene_nodes for l in s.links if l.type == 'node'])
        return incidents.merge(links, how='left', on='incident_ref')\
                            .merge(scenes, how='left', on='scene_ref')\
                            .merge(docs, how='left', on='filepath').fillna('No Data').drop_duplicates()

    def search(self, **kw):
        field, pat = next((k,v) for k,v in kw.items())
        query = f'{field}.str.contains("{pat}", case=False)'
        return self.df.query(query)[['story', 'incident', 'scene', 'date_string']]
    
    def unplaced_incidents(self):
        self.df[self.df.scene == 'No Data'][['story', 'incident']]
    
    
    def unlinked_scenes(self):
        def scene_node_data(scene_node):
                doc =  Document.read_file(scene_node.document_link)
                return dict(scene=scene_node.name, date=date_parse(doc.metadata['date']))
        
        return pd.DataFrame([scene_node_data(n)
                            for n in self.ct.nodes('Scenes') \
                            if n.document_link \
                            if not any(l for l in n.links if l.type == 'node')])

    def broken_links(self):
        for node in [n for n in self.ct.nodes('Scenes') if n.document_link]:
            for link in [l for l in node.links if l.type == 'node']:
                try:
                    self.ct.find_node_by_id(link.href).name
                except AttributeError:
                    yield 'broken link at', node.name

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


    
