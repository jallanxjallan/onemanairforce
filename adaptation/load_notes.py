#!/home/jeremy/Python3.7Env/bin/python
# -*- coding: utf-8 -*-
#
#  script.py
#
#  Copyright 2019 Jeremy Allan <jeremy@jeremyallan.com>


from storage.cherrytree import CherryTree
from document.document import Document
from utility.config import load_config
from utility.strings import snake_case
from utility.helpers import make_identifier
from IPython.display import Markdown as md
from pathlib import Path
from functools import reduce
from collections import Counter
# from document.pandoc import PandocArgs, run_single
import dateutil
import datetime
import pandas as pd
import spacy
import attr
import re
import redis

DEFAULT_DATE=datetime.date(1988, 1, 4)
nlp = spacy.load('en_core_web_md')

def make_df_row(d):
    doc, node = d
    if not node.notes:
        return None 
    
    dateref = next((e.text for e in doc.ents if e.label_ == 'DATE'), None)
    try:
        datestamp = dateutil.parser.parse(dateref, default=DEFAULT_DATE) 
    except:
        datestamp = None
    
    return dict(
        name=node.name,
        identifier=node.id,
        parent=node.parent.id,
        level=node.level,
        story=node.parent.name,
        date_ref=dateref,
        datestamp=datestamp,
        notes= node.notes)

def story_link(link):
    return dict(
        sequence=link.parent_node.name,
        identifier=link.href
    )

def story_placements(index_file):

    ct = CherryTree(index_file) 
    
    docs = nlp.pipe([(n.notes, n) for n in ct.nodes("Stories") 
                     if n.level > 2 
                     if not n.name.startswith('~')], as_tuples=True)
    
    dfn = pd.DataFrame(filter(None, [make_df_row(d) for d in docs])) 
                              
    dfl = pd.DataFrame([story_link(l) for n in ct.nodes('Synopsis') for l in n.links if l.type == 'node'])
    dfl['sequence_no'] = dfl.index.values
    df = dfn.merge(dfl, how='left', on='identifier')
    df.sequence.fillna('Unplaced', inplace=True)
    df.sequence_no.fillna(0, inplace=True)
    return df
