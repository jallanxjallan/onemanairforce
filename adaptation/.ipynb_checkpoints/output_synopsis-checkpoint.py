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
from document.pandoc import PandocArgs, interfile, temp_content, run_pandoc


def output_synopsis(output_file, doc_index='synopsis.ctd', base_node='Synopsis'):
    ct = CherryTree(doc_index)
    args = []
    for link in [l for n in ct.nodes(base_node) for l in n.links]:
        link_args = dict(
            output=interfile(),
            template='scene',
            filters=['strip_codeblocks.lua']
        )


        ref_node = ct.find_node_by_id(link.href)
        if not ref_node:
            print('no reference for', link.text)
            continue

        ref_link = next(
            (l for l in ref_node.links if l.href == ref_node.filepath), None)
        if not ref_link:
            print(ref_node.name, 'has no file link')
            continue

        link_args['input'] = ref_link.href

        if list(ref_node.ancestors)[-1].name == 'Interviews':
            link_args['filters'].append('select_by_header.lua')
            link_args['metadata'] = dict(section_heading=ref_node.name)

        args.append(PandocArgs(**link_args))



    rs = run_pandoc(args)

    print(rs)

    a = PandocArgs(
        inputs=[a.output for a in args],
        output=Path('output', output_file)
    )

    print(run_pandoc(a))


if __name__ == '__main__':
    fire.Fire(output_synopsis)
