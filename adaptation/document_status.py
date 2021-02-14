import sys
import pandas as pd
from storage.cherrytree import CherryTree
from document.document import Document
from utility.config import load_config
import dateparser

def load_status_data(index_file=None, base_node=None):
    cf = load_config()
    ct = CherryTree(index_file or cf['index-file'])

    return pd.DataFrame([dict(node=n, doc=Document.read_file(n.filepath))
            for n in ct.nodes(base_node or cf.get('base-node', None))
            if n.filepath]).fillna('No Data')
