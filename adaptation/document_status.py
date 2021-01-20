import sys
import pandas as pd
from pathlib import Path
from storage.cherrytree import CherryTree
from utility.config import load_config
import sys
import redis
import dateparser

cf = load_config()
namespace = cf.get('namespace', 'document')
base_node = cf.get('base-node', None)
r = redis.Redis(decode_responses=True)

def load_status_data():
    ct = CherryTree(cf['index-file']) 
    di = f'{namespace}:filepath.document:index'
    data = []
    for node in [n for n in ct.nodes(base_node) if n.filepath]:
        dk = r.hget(di, node.filepath)
        if dk:
            item = {**{'name':node.name, 'level':node.level}, **r.hgetall(dk)}
            data.append(item)
        else:
            print(dk, 'not found')
    
    return pd.DataFrame(data).fillna('No Data')
    
