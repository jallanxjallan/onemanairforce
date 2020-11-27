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


sys.path.append('/home/jeremy/Library')
from storage.cherrytree_xml import CherryTree
from document.document import Document
from utility.helpers import make_identifier, snake_case

note_split = re.compile(r'~+')
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


def make_synopsis(doc_index, output, base_node=None):
    ct = CherryTree(doc_index)
    content = []
    for node in ct.nodes(base_node):
        notes = node.notes.split("\n")
        if len(notes) > 2:
            print(notes)
            break

        for link in [l for l in node.links if l.type == 'node']:
            ref_node = ct.find_node_by_id(link.href)
            try:
                intro, text = note_split.split(ref_node.notes, maxsplit=2)
            except ValueError:
                continue
            content.append(text)
    Document(content='\n'.join(content)).write_document(output=output)

    #     # filepath = next((l.href for l in node.links if l.type == 'file'), None)
        # if filepath:
        #     rs = move_story(node, filepath)
        # else:
        #     rs = export_story(node)
        # if not rs:
        #     continue
        # identifier, outputfile = rs
        # [e.getparent().remove(e) for e in node.element.iterchildren('rich_text')]
        # anchor = node.insert_anchor(identifier)
        # node.insert_link(href=outputfile, text="Content")
        # print (f'Notes from {node.name} written to {outputfile}')
if __name__ == '__main__':
    fire.Fire(make_synopsis)
