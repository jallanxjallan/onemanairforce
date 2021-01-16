#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from utility.helpers import snake_case
import pandas as pd
import shutil
from pathlib import Path
from storage.cherrytree import CherryTree
import sys
sys.path.append('/home/jeremy/Library')
target_dir = Path('scenes')


def scene_links(story):
    ct = CherryTree('synopsis.ctd')
    story_node = ct.find_node_by_name(story)
    scene_node = ct.find_node_by_name('Scenes')
    story_links = pd.DataFrame([dict(Scene=n.name, href=l.href)
                                for n in scene_node.descendants
                                for l in n.links if l.type == 'node'])
    story_nodes = pd.DataFrame([dict(Story=n.name, href=n.id)
                                for n in story_node.descendants])

    df = story_nodes.merge(story_links, how='left', on='href')[
        ['Story', 'Scene']]
    return df.fillna('Unplaced')


def file_matches():
    ct = CherryTree('synopsis.ctd')
    nodes = set([n.filepath for n in ct.nodes(
        'Flight To Tasik') if n.filepath])
    files = set([str(f) for f in Path('scenes').iterdir()])
    return [f for f in nodes.difference(files) if f.endswith('.md')]
