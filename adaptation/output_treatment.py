#!/home/jeremy/Python3.6Env/bin/python
# -*- coding: utf-8 -*-
#
#  script.py
#  
#  Copyright 2019 Jeremy Allan <jeremy@jeremyallan.com>

import sys 
import os
import plac
from pathlib import Path
import yaml

sys.path.append('/home/jeremy/Library')

from storage.cherrytree_xml import CherryTree
from document import file_to_text, text_to_file 

metadata = dict(doc_separator='date --- location')

def main(source_index, outputfile, rootnode='Scenes'):
    base_path = Path.cwd()
    ct = CherryTree(source_index)
    scene_base = ct.find_node_by_name(rootnode)
    output_texts = []

    for node in scene_base.descendants:
        treatment_link = next((l for l in node.links if l.text == 'Treatment'), None)
        
        if not treatment_link:
            continue
        
        
        # exception is logged and function returns None
        text = file_to_text(treatment_link.filepath, metadata=metadata)
        if text:
            output_texts.append(text)
            break
    
    rs = text_to_file(output_texts, outputfile)
    print(rs)
        
    
if __name__ == '__main__':
    plac.call(main)
