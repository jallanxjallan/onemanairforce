#!/home/jeremy/Python3.7Env/bin/python
# -*- coding: utf-8 -*-
#
#  script.py
#
#  Copyright 2019 Jeremy Allan <jeremy@jeremyallan.com>



from document.document import Document
from document.pandoc import PandocArgs
from pathlib import Path
from storage.cherrytree import CherryTree
from utility.strings import snake_case
from collections import defaultdict
import fire




def create_sequences(index_file, base_node='Synopsis'):
    ct = CherryTree(index_file) 
    sequences = defaultdict(list)
    for node, link in [(n, l) for n in ct.nodes(base_node) 
        for l in n.links if l.type == 'node'
        if not any(l for l in n.links if l.text == 'Sequence')]:
        try:
            sequences[node.name].append(ct.find_node_by_id(link.href).content) 
        except Exception as e:
            print(e)
    for name, contents in sequences.items():
        print(PandocArgs(input=contents, output=snake_case(name)))


if __name__ == '__main__':
    fire.Fire(create_sequences)


'''
outputfile = Path('output').joinpath(snake_case(episode)).with_suffix('.md')
    
    nodes = [n for n in ct.nodes(episode) if n.content]
    scene_meta = make_scene_meta(nodes, ct)
    content = []
    for i in range(len(nodes)):
        prev_node = nodes[i-1] if i > 0 else None
        next_node = nodes[i+1] if i < len(nodes) -1 else None
        node = nodes[i]

        if not prev_node:
            content.append(node.content)
        elif not next_node:
            content.append(node.content)

        elif node.level == 4:
             content.append(f'**In a flashback to** {node.content}')
        elif prev_node.level == 4 and next_node.level  == 4:
             content.append(f'**Returning to the interview** {node.content}')
        else:
             content.append(node.content)
    rs = run_pandoc(PandocArgs(text=content, output=outputfile))
    print(rs.errors)
    
'''
