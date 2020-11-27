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


from storage.cherrytree import CherryTree
from document.pandoc import PandocArgs, interfile, run_pandoc
from utility.helpers import snake_case


def output_synopsis(base_node_name, doc_index):

    ct = CherryTree(doc_index)
    args = []
    base_node = ct.find_node_by_name(base_node_name)
    if not base_node:
        print (base_node_name, 'not found')
        exit()

    for node in [n for n in base_node.descendants if n.filepath]:

        args.append(PandocArgs(
                    input=node.filepath,
                    output=interfile(),
                    metadata=dict(section_heading='Synopsis'),
                    template='synopsis',
                    filters=['strip_codeblocks.lua',
                             'format_slugline.py'
                             ]
            ))


    args.append(PandocArgs(
        inputs=[a.output for a in args],
        output=Path('output', snake_case(base_node.name)).with_suffix('.md'),
        filters=['strip_duplicate_headers.lua']
    ))


    print(run_pandoc(args))

if __name__ == '__main__':
    fire.Fire(output_synopsis)
