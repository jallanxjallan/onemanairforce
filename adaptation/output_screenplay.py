#!/home/jeremy/Python3.7Env/bin/python
# -*- coding: utf-8 -*-
#
#  script.py
#
#  Copyright 2019 Jeremy Allan <jeremy@jeremyallan.com> 


from pathlib import Path
from storage.cherrytree import CherryTree
from storage.redis import rds, RedisKey
from document.pandoc import PandocArgs
from dateutil.parser import parse as date_parse
import fire 
import re 
import uuid



def output_synopsis(index_file, output_file):
    ct = CherryTree(index_file) 
    rkey = RedisKey(namespace='omaf', component='slugline.data')
    for i, story_node in enumerate([ct.find_node_by_id(l.href) 
        for n in ct.nodes('Synopsis') 
        for l in n.links(type='node')]): 
        if not any(story_node.links(type='file')):
            continue 
        try:
            previous_sibling_key = str(rkey(story_node.previous_sibling.id)) 
        except AttributeError: 
            previous_sibling_key = str(rkey(0))
            
            
        data = dict(
            previous_sibling_key=previous_sibling_key,
            parent_key=str(rkey(story_node.parent.id)),
            level=story_node.level,
            name=story_node.name,
            id=story_node.id
            )
        story_key = str(rkey(story_node.id))
        [rds.hset(story_key,k,v) for k,v in data.items()] 
        rds.expire(story_key, 120)
        print(PandocArgs(input=next(story_node.links(type='file')).href,
                metadata=dict(slugline_data_key=story_key),
                filters=['insert_slugline.lua', 'print_output_file.lua']))
        if i > 2:
            pass
            
            
if __name__ == '__main__':
    fire.Fire(output_synopsis)
    
    
