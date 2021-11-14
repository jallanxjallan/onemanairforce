#!/home/jeremy/Python3.7Env/bin/python
# -*- coding: utf-8 -*-
#
#  script.py
#
#  Copyright 2019 Jeremy Allan <jeremy@jeremyallan.com> 
import sys
from pathlib import Path
from storage.cherrytree import CherryTree
from document.document import Document
from utility.strings import snake_case, title_case
import pandas as pd 
from sqlalchemy import create_engine
import fire
 

def archive_document(filepath):
    fp = Path(filepath) 
    if not fp.suffix.lower() in ('.md', '.txt'):
        return None
    try:
        content = fp.read_text()
    except Exception as e:
        print(e) 
        return None
    return dict(source=fp.stem, content=content)
       
def archive_documents(outputfile):

    engine = create_engine(f'sqlite:///{outputfile}', echo=False) 
    
    df = pd.DataFrame(filter(None, [archive_document(f.strip()) for f in sys.stdin.readlines()]))

    with engine.begin() as connection:
        df.to_sql('document', con=connection, if_exists='append') 
    
    
if __name__ == '__main__':
    fire.Fire(archive_documents)
    
    
