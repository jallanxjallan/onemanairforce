#!/home/jeremy/Python3.7Env/bin/python
# -*- coding: utf-8 -*-
#
#  script.py
#
#  Copyright 2019 Jeremy Allan <jeremy@jeremyallan.com>


from collections import defaultdict
from document.document import Document
from document.pandoc import PandocArgs, run_pandoc
from pathlib import Path
from spacy.language import Language
from spacy.tokens import Span
from storage.cherrytree import CherryTree
from utility.config import load_config
from utility.strings import snake_case
import fire
import pandas as pd
import re
import spacy
import yaml
import attr

@attr.s
class SceneMeta():
    datestamp = attr.ib(default=None)
    relative = attr.ib(default=None)
    location = attr.ib(default=None)
    character = attr.ib(default=None)


ent_fields = ('DATESTAMP', 'RELATIVE', 'CHARACTER', 'LOCATION')

@Language.component("scene_datestamp")
def scene_datestamp(doc):
    new_ents = []
    for ent in doc.ents:
        if ent.label_ == 'DATE':
            if  re.match('\d*\s\w+\s\d{4}', ent.text):
                new_ents.append(Span(doc, ent.start, ent.end, label='DATESTAMP'))
            else:
                new_ents.append(Span(doc, ent.start, ent.end, label='RELATIVE'))
        else:
            new_ents.append(ent)
    doc.ents = new_ents
    return doc

def make_character_pattern(name):
    name_pats = '|'.join(name.split())
    pattern = {'TEXT': {'REGEX': f'({name_pats})'}}
    return {'id':snake_case(name), "label": "CHARACTER", "pattern": [pattern]}

def make_location_pattern(name):
    pattern = {'LOWER': name.lower()}
    return {'id':snake_case(name), "label": "LOCATION", "pattern": [pattern]}


def make_scene_meta(nodes, ct):
    scene_meta = {}
    nlp = spacy.load('en_core_web_md')
    nlp.disable_pipe("parser")
    nlp.enable_pipe("senter")
    ner_config = {
       "phrase_matcher_attr": None,
       "validate": True,
       "overwrite_ents": False,
       "ent_id_sep": "||"
    }
    ruler = nlp.add_pipe("entity_ruler", config=ner_config, before='ner')
    ruler.add_patterns([make_character_pattern(n.name) for n in ct.nodes('Characters')])
    ruler.add_patterns([make_location_pattern(n.name) for n in ct.nodes('Locations')])

    nlp.add_pipe("scene_datestamp", after="ner")

    for doc, node_id in nlp.pipe([(n.content, n.id) for n in nodes], as_tuples=True):
        data = defaultdict(list)
        [data[e.label_.lower()].append(e.text) for e in doc.ents if e.label_ in ent_fields]
        scene_meta[node_id] = SceneMeta(**data)

    return scene_meta



def output_synopsis(episode):
    outputfile = Path('output').joinpath(snake_case(episode)).with_suffix('.md')
    ct = CherryTree('synopsis.ctd')
    nodes = [n for n in ct.nodes(episode) if n.content]
    scene_meta = make_scene_meta(nodes, ct)
    content = []
    for i in range(len(nodes)):
        prev_node = nodes[i-1] if i > 0 else None
        next_node = nodes[i+1] if i < len(nodes) -1 else None
        node = nodes[i]

        if not prev_node:
            content.append(node.content)
        elif not next_node:
            content.append(node.content)

        elif node.level == 4:
             content.append(f'**In a flashback to** {node.content}')
        elif prev_node.level == 4 and next_node.level  == 4:
             content.append(f'**Returning to the interview** {node.content}')
        else:
             content.append(node.content)
    rs = run_pandoc(PandocArgs(text=content, output=outputfile))
    print(rs.errors)



if __name__ == '__main__':
    fire.Fire(output_synopsis)



