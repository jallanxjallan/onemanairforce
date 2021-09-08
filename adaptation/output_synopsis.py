#!/home/jeremy/Python3.7Env/bin/python
# -*- coding: utf-8 -*-
#
#  script.py
#
#  Copyright 2019 Jeremy Allan <jeremy@jeremyallan.com>

from storage.cherrytree import CherryTree
from utility.config import load_config
from document.pandoc import PandocArgs, run_pandoc
from document.document import Document
import fire
import yaml
import re

def output_synopsis(outputfile):
    ct = CherryTree('synopsis.ctd')
    pandoc_args = []
    
    for node in [n for n in ct.nodes('Episodes') if n.level > 1]:
        if node.name == 'Episode 2':
            break
        if node.level == 2:
            pandoc_args.append(PandocArgs(
                metadata=dict(episode=node.name)))
       
        else:
            node_args = PandocArgs(
                input=node.document_link,
                filters=['insert_slugline_args.lua']) 
            try:
                wrap_scene = next(filter(lambda x: x in ('Interviews', 'Writings'), \
                                [ct.find_node_by_id(l).ancestors[0].name \
                                for l in node.node_links]), None)
            except Exception as e: 
                print(e)
                wrap_scene = None
            if wrap_scene:
                node_args.metadata=dict(wrap_scene=wrap_scene)
            

            pandoc_args.append(node_args)

    pandoc_args.append(PandocArgs(inputs=pandoc_args,
                                  output=outputfile,
                                  standalone=False,
                                  filters=['format_slugline.py'])) 
    
    rs = run_pandoc(pandoc_args, debug=False)
    print(rs)


if __name__ == '__main__':
    fire.Fire(output_synopsis) 
    
    
'''
    
'''                                  
