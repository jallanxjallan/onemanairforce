#!/home/jeremy/Python3.6Env/bin/python
# -*- coding: utf-8 -*-
#
#  script.py
#
#  Copyright 2019 Jeremy Allan <jeremy@jeremyallan.com>

import sys
import os
import re
import fire
from pathlib import Path


sys.path.append('/home/jeremy/Library')
from storage.cherrytree_xml import CherryTree
from pandoc.pandoc_convert import PandocArgs


def export_synopsis(doc_index='synopsis.ctd', base_node='Sequences'):
    ct = CherryTree(doc_index)
    staging_path = Path('staging')
    for node_seq, node in enumerate(ct.nodes(base_node)):
        for link_seq, ref_node_id in enumerate([l.href for l in node.links if l.type == 'node']):
            ref_node = ct.find_node_by_id(ref_node_id)
            seq = (node_seq * 100) + link_seq
            if ref_node and ref_node.filepath:
                print(PandocArgs(
                    input=ref_node.filepath,
                    output=str(staging_path.joinpath(str(seq).zfill(5)).with_suffix('.md')),
                    defaults='create_synopsis'
                )
                     )
                

if __name__ == '__main__':
    fire.Fire(export_synopsis)
