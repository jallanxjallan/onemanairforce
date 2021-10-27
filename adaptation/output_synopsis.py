#!/home/jeremy/Python3.7Env/bin/python
# -*- coding: utf-8 -*-
#
#  script.py
#
#  Copyright 2019 Jeremy Allan <jeremy@jeremyallan.com>


from collections import defaultdict
from document.document import Document
from document.pandoc import PandocArgs, run_pandoc
from pathlib import Path
from storage.cherrytree import CherryTree
from utility.strings import snake_case
import fire




def output_synopsis(episode):
    outputfile = Path('output').joinpath(snake_case(episode)).with_suffix('.md')
    ct = CherryTree('synopsis.ctd')
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



if __name__ == '__main__':
    fire.Fire(output_synopsis)



