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
from document.pandoc import PandocArgs, dump_pandoc, interfile

def export_synopsis(doc_index='treatment.ctd', base_node='Scenes'):
    current_level = 3
    def mtext(node):
        nonlocal current_level
        if node.level == current_level:
            prefix = ''
        elif node.level == 3:
            prefix = '**In 1988**'
        elif node.level == 4:
            prefix = '**In a flashback**'
        current_level = node.level
        return f'{prefix} {node.content}'

    ct = CherryTree(doc_index)

    # content = [f'**{n.name}**: {n.content}' for n in ct.nodes(base_node) if n.content]
    content = [n.content for n in ct.nodes(base_node) if n.content]
    print(PandocArgs(
        input=interfile('\n\n'.join(content)),
        output='output/one_man_air_force_synopsis.docx',
        fr='markdown')
    )


if __name__ == '__main__':
    fire.Fire(export_synopsis)
