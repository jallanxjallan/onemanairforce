#!/home/jeremy/Python3.6Env/bin/python
# -*- coding: utf-8 -*-
#
#  script.py
#  
#  Copyright 2019 Jeremy Allan <jeremy@jeremyallan.com>

import sys 
import os
import re
import plac
from pathlib import Path
import pypandoc
from bs4 import BeautifulSoup

node_pat = re.compile('node')
soup = None

def parse_node_text(node):
    if not node:
        return False
    text_elements = node('rich_text')
    for text_element in text_elements:
        try:
            text_element['link'] == node_pat
            node_id = text_element['link'].split()[1]
            linked_node = soup.find('node', {'unique_id':node_id})
            for line in parse_node_text(linked_node):
                yield line
        except KeyError:
            yield text_element.string

def main(source, outfile):
    global soup
    spath = Path(source)
    soup = BeautifulSoup(spath.read_text(), 'lxml')
    
    output_lines = []
    scenes = soup.find('node', {'name':'Scenes'})
    for scene in scenes('node'):
        for line in parse_node_text(scene):
            output_lines.append(line)
    pypandoc.convert_text('\n'.join(output_lines), 
                        'markdown', 
                        format='markdown',
                        outputfile='treatment_draft.md'
                    )
if __name__ == '__main__':
    plac.call(main)
