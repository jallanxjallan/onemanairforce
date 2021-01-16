#!/usr/bin/env python

import pandas as pd
from pathlib import Path
from storage.cherrytree import CherryTree
import sys

def story_placements(story_node, scenes_node, index_file):
    ct = CherryTree(index_file)
    story_node = ct.find_node_by_name(story_node)
    scene_node = ct.find_node_by_name(scenes_node)
    story_links = pd.DataFrame([dict(Scene=n.name, href=l.href, sc_no=no)
                                for no, n in enumerate(scene_node.descendants)
                                for l in n.links if l.type == 'node'])
    story_nodes = pd.DataFrame([dict(Story=n.name, href=n.id, st_no=no)
                                for no, n in enumerate(story_node.descendants)])

    df = story_nodes.merge(story_links, how='left', on='href')
    return df.fillna('Unplaced')[['Story', 'Scene']]
