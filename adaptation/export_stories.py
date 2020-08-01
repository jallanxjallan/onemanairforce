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
from subprocess import run, Popen, PIPE

sys.path.append('/home/jeremy/Library')
from storage.cherrytree_xml import CherryTree
from utility.helpers import make_identifier, snake_case

doc_index = 'synopsis.ctd'
target_dir = Path('events')
base_node = 'Events'

def create_file(output, node, input=None, content=None):
    identifier = make_identifier()
    args = ['pandoc',
            '--defaults=create_story',
            f'--output={str(output)}',
            f'--metadata=title:{node.name}',
            f'--metadata=identifier:{identifier}']
    if input:
        args.append(str(input))
        run(args)
    elif content:
        p = Popen(args, stdin=PIPE)
        rs = p.communicate(input=content, timeout=5)
    return identifier, output

def move_story(node, filepath):
    inputfile = Path(filepath)
    outputfile = target_dir.joinpath(inputfile.name)
    return create_file(outputfile, node, input=inputfile)


def export_story(node):
    text = '\n'.join(list(node.texts))
    if len(text) < 10:
        return False

    try:
        content = re.split('\~+', text)[1].encode('utf-8')
    except IndexError:
        content = text.encode('utf-8')

    if len(content) < 10:
        return False


    outputfile = target_dir.joinpath(snake_case(node.name)).with_suffix('.md')

    return create_file(outputfile, node, content=content)


def export_stories():
    ct = CherryTree(doc_index)
    for node in ct.nodes(base_node):
        filepath = next((l.href for l in node.links if l.type == 'file'), None)
        if filepath:
            rs = move_story(node, filepath)
        else:
            rs = export_story(node)
        if not rs:
            continue
        identifier, outputfile = rs
        [e.getparent().remove(e) for e in node.element.iterchildren('rich_text')]
        anchor = node.insert_anchor(identifier)
        node.insert_link(href=outputfile, text="Content")
        print (f'Notes from {node.name} written to {outputfile}')
    ct.save()
if __name__ == '__main__':
    fire.Fire(export_stories)
