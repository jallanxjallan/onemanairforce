#!/home/jeremy/Python3.7Env/bin/python
# -*- coding: utf-8 -*-
#
#  script.py
#
#  Copyright 2019 Jeremy Allan <jeremy@jeremyallan.com>

import pandas as pd
import re
from collections import Counter
from pathlib import Path
from storage.cherrytree import CherryTree
from document.document import Document
from dateutil.parser import parse as parse_date
from fuzzywuzzy import process, fuzz
from utility.strings import snake_case
import fire

INDEX_FILE = 'screenplay.ctd'
SCENE_NODE = 'Scenes'
STORY_NODE = 'Stories'
DOCUMENT_DIR = 'scenes'

def get_scene(node, ct):
    try:
        scene = ct.parent(next(ct.find_node_links(node.id))).name
    except Exception as e:
        scene = None
    return scene

def incident_data(ct, node):
    return dict(
        story=ct.ancestors(node)[1].name,
        incident=node.name,
        scene=get_scene(node, ct)
    )

def scene_data(ct, node):
    try:
        doc = Document.read_file(node.document_link)
    except Exception as e:
        print(f'{e} at {node.name}')
        return None
    try:
        data = {**dict(scene=node.name,
                    sequence=ct.ancestors(node)[1].name if node.level > 2 else node.name,
                    level=node.level,
                    datestamp=parse_date(doc.metadata['date'])),
            **doc.asdict()
            }
    except Exception as e:
        print(f'{e} at {node.name}')
        return None 
    return data


class Outliner():
    def __init__(self):
        ct = CherryTree(INDEX_FILE)
        dfd = pd.DataFrame(filter(None, [scene_data(ct, s) for s in ct.nodes(SCENE_NODE) if s.document_link]))
        dfd['scene_no'] = dfd.index
        dfs = pd.DataFrame(filter(None, [incident_data(ct, n) for n in ct.nodes(STORY_NODE) if n.notes]))
        dft = dfs.merge(dfd, how='left', on='scene').sort_values('scene_no')
        self.df = dft[dft.status != 'drop']
        self.ct = ct

    @property
    def synopsis(self):
        for r in self.df.drop_duplicates(subset=['scene']).itertuples():
            if not r.status == 'synopsis':
                continue
            synopsis = r.content.split('------')[0]

            try:
                print(f'**{r.scene} - {r.date}**:  {synopsis.lstrip()}')
            except Exception as e:
                print(f'Cannot display {r.scene} because {e}')

    @property
    def outline(self):
        columns = [c for c in ('source', 'story', 'incident', 'sequence','scene', 'date', 'category', 'status') if c in self.df.columns]
        print(self.df.sort_values('scene_no')[columns])


    def mentions(self, *pats):
        query = [f'(content.str.contains("{p}", case=True))' for p in pats]
        self.df = self.df.dropna(subset=['content']).query(' & '.join(query))
        return self


    def story(self, *stories):
        pats = '|'.join(stories)
        self.df = self.df.query(f'story.str.contains("{pats}")')
        return self

    def sequence(self, name):
        dft = self.df.dropna(subset=['sequence'])
        self.df = dft[dft.sequence.str.contains(name)]
        return self

if __name__ == '__main__':
        fire.Fire(Outliner)
