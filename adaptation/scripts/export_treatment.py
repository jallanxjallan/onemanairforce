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
    args = []
    for node in ct.nodes(base_node):
        if node.filepath:
            args.append(PandocArgs(
                input=node.filepath,
                output=interfile(),
                filters=['insert_metadata_ref.lua', 'strip_codeblocks.lua']
            ))
        elif node.content:
            args.append(PandocArgs(
                    input=interfile(node.content),
                    output=interfile(),
                    fr='markdown'))
        else:
            continue

    args.append(PandocArgs(
        inputs=[a.output for a in args],
        output='output/treatment.docx',
        filters='format_slugline.py'
    ))

    dump_pandoc(args)


if __name__ == '__main__':
    fire.Fire(export_synopsis)
