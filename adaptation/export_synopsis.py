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
    ct = CherryTree(doc_index)
    print(PandocArgs(
        inputs=[interfile(f'**{n.name}**: {n.content}')
                for n in ct.nodes(base_node) if n.content],
        output='output/synopsis.docx',
        fr='markdown')
    )


if __name__ == '__main__':
    fire.Fire(export_synopsis)
