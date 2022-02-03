#!/home/jeremy/Python3.7Env/bin/python
# coding: utf-8



from pathlib import Path
import fire

from document.document import Document 
from storage.cherrytree import CherryTree 
import spacy 
               
def highlight_dates(index_file, base_node=None, label='sequence'):
    op = Path('staging')
    ct = CherryTree(index_file) 
    nlp = spacy.load('en_core_web_md')
    nlp.disable_pipe("parser")
    nlp.enable_pipe("senter")
    
    source_docs = [Document.read_file(n.document_link(label)) for n in ct.nodes() if n.document_link(label)] 
    for doc, source_doc in nlp.pipe([(sd.content, sd) for sd in source_docs], as_tuples=True):
        no_replacements = 0
        for ent in [e for e in doc.ents if e.label_ == 'DATE']:
           source_doc.content = source_doc.content.replace(ent.text, f'**{ent.text}**') 
                                
           no_replacements += 1 
        if no_replacements > 0:
            print(f'Replaced {no_replacements} entities in {source_doc.filepath.stem}')
            source_doc.write_file(op.joinpath(source_doc.filepath.name)) 
        
if __name__ == '__main__':
    fire.Fire(highlight_dates)



