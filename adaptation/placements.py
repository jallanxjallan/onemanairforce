#!/home/jeremy/Python3.7Env/bin/python
# -*- coding: utf-8 -*-
#
#  script.py
#
#  Copyright 2019 Jeremy Allan <jeremy@jeremyallan.com>

from storage.cherrytree import CherryTree
import pandas as pd
import dateutil
import datetime
import fire 

DEFAULT_DATE=datetime.date(1988, 1, 4)
def story_node(node):
    if not node.notes:
        return None
    try:
        datestamp = dateutil.parser.parse(next(node.bullets), default=DEFAULT_DATE) 
    except Exception as e:
        print(e) 
        return None
    return dict(
        story=node.parent.name,
        incident=node.name,
        datestamp=datestamp,
        identifier=node.id) 

def story_link(link):
    return dict(
        sequence=link.parent_node.name,
        identifier=link.href
    )

def story_placements(index_file):

    ct = CherryTree(index_file) 
    stories = [n for n in ct.nodes('Stories') if n.level == 2] 
    for no, node in enumerate(stories):
        print(f'{no+1}. {node.name}')
    selections = input('Select stories: ') 
    
    dfn = pd.DataFrame(filter(None, [story_node(n)  
                                        for s in selections.split() 
                                        for n in ct.nodes(stories[int(s)-1])
                                        if n.level > 2]))
                                        #if not n.name == stories[int(s-1)].name) 
    dfn['date'] = dfn.datestamp.apply(lambda x: x.strftime('%B %Y') if x.day == 4 else x.strftime('%d %B %Y'))
                                            
    dfl = pd.DataFrame([story_link(l) for n in ct.nodes('Synopsis') for l in n.node_links])
    dfl['sequence_no'] = dfl.index.values
    df = dfn.merge(dfl, how='left', on='identifier')
    df.sequence.fillna('Unplaced', inplace=True)
    df.sequence_no.fillna(0, inplace=True)
    dfs = df.sort_values('sequence_no')
    
    print(dfs[['story', 'incident', 'date', 'sequence']])
    
if __name__ == '__main__':
    fire.Fire(story_placements)
