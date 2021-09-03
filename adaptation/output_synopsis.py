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

def output_synopsis(episode, outputfile):
    ct = CherryTree('synopsis.ctd')
    pandoc_args = []
    sequence_start = False
    for node in [n for n in ct.nodes('Episodes']:
        if node.level == 2:
            pandoc_args.append(PandocArgs(text=node.name, template='synopsis'))
            continue
        elif node.level == 3:
            sequence_start = True
            continue
        else:
            node_args = PandocArgs(filters=['format_slugline.py'],
                                   template='scene',
                                   metadata=dict(
                                       metadata_index_key='omaf:metadata:index',
                                       sequence_start=sequence_start)
                                   )

            if node.document_link:
                node_args.input = node.document_link
            elif node.content:
                codebox = next(scene.codeboxes)
                for k,v in yaml.safe_load(codebox.content).items():
                    node_args.metadata[k] = v 
                node_args.text = scene.content

            pandoc_args.append(node_args)


    pandoc_args.append(PandocArgs(inputs=pandoc_args, output=outputfile, standalone=False))
    rs = run_pandoc(pandoc_args, debug=False)
    print(rs)


if __name__ == '__main__':
    fire.Fire(output_synopsis)
