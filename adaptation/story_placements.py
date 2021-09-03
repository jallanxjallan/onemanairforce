    #%%writefile scripts/story_placements.py
    #!/usr/bin/env python

import pandas as pd
from pathlib import Path
from storage.cherrytree import CherryTree
import dateparser
import fire

# def get_timestamp(node):
#     return next(filter(None, (dateparser.parse(b) for b in node.bullets)), None )

def story_placements(content_index, story_node):
    ct = CherryTree(content_index)
    data = []

    for seq, story_node in enumerate([n for n in ct.nodes(story_node) if n.level == 3]):
        # timestamp = get_timestamp(node) or dateparser.parse('1 January 2020')
        item = dict(incident=story_node.name, seq = seq)

        episode_node = ct.find_elem_by_attribute('link', f'node {story_node.id}')
        if episode_node:
            item['episode'] = episode_node.ancestors[1].name
            item['scene']   = episode_node.name

        data.append(item)

    df = pd.DataFrame(data).fillna('Unplaced')

    print(df[['incident', 'seq', 'episode', 'scene']].sort_values('episode'))

if __name__ == '__main__':
    fire.Fire(story_placements)
