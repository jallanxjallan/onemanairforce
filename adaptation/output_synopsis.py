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
    sequence_start = False
    for node in [n for n in ct.nodes('Episodes') if n.level > 1]:
        if node.name == 'Episode 2':
            break
        if node.level == 2:
            pandoc_args.append(PandocArgs(
                metadata=dict(episode=node.name)))
            continue
        elif node.level == 3:
            sequence_start = True
            continue
        else:
            node_args = PandocArgs(filters=['insert_slugline_args.lua'],
                                   metadata=dict(sequence_start=sequence_start)
                                   )

            if node.document_link:
                node_args.input = node.document_link
            elif node.content:
                codebox = next(node.codeboxes, None)
                if not codebox:
                    continue
                for k,v in yaml.safe_load(codebox.content).items():
                    node_args.metadata[k] = v
                node_args.text = node.content

            pandoc_args.append(node_args)
            sequence_start = False

    pandoc_args.append(PandocArgs(inputs=pandoc_args,
                                  output=outputfile,
                                  standalone=False,
                                  filters=['format_slugline.py']))
    rs = run_pandoc(pandoc_args, debug=False)
    print(rs)


if __name__ == '__main__':
    fire.Fire(output_synopsis)
