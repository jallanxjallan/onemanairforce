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
from collections import defaultdict


def is_wrap_scene(scene, ct):
    
    return next((n.ancestors[0].name for n in ct.linked_nodes(scene) 
        if n 
        if n.ancestors[0].name in ('Interviews', 'Writings')), None)
        


def output_synopsis(outputfile):
    ct = CherryTree('synopsis.ctd')
    pandoc_args = []
    episodes = defaultdict(list) 
    
    
    [episodes[s.ancestors[1].name].append(s) for s in ct.nodes('Episodes') if s.document_link] 
    
    
    for episode, scenes in episodes.items():
        pandoc_args.append(PandocArgs(metadata=dict(episode=episode))) 
           
        for scene in scenes: 
            scene_args = PandocArgs(input=scene.document_link,filters=['insert_slugline_args.lua']) 
            
            wrap_scene = is_wrap_scene(scene, ct)
            
            if wrap_scene:
                scene_args.metadata=dict(wrap_scene=wrap_scene)
            

            pandoc_args.append(scene_args) 
    pandoc_args.append(PandocArgs(inputs=pandoc_args,
                                  output=outputfile,
                                  standalone=False,
                                  filters=['format_slugline.py'])) 
            
    
    rs = run_pandoc(pandoc_args, debug=False)
    print(rs)


if __name__ == '__main__':
    fire.Fire(output_synopsis) 
    
    
'''
                
            
       
        else:
           
            

    

'''                                  
