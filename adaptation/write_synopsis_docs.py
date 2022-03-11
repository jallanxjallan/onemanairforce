from storage.cherrytree import CherryTree
from document.document import Document
import re

def get_synopsis(node):
    link = next(node.links(type='file', label="Treatment"), None) 
    if not link:
        return None
    doc = Document.read_file(link.href)
    
   
    try: 
        synopsis = doc.synopsis.lstrip('\n') 
    except:
        synopsis = doc.content.lstrip('\n') 

    try:
        date = doc.metadata["date"]
    except KeyError: 
        date = 'No Date Found'
    return f'[{node.name}]{{cat="scene"}}[{date}]{{cat="date"}}  {synopsis}'

ct = CherryTree('screenplay.ctd')
for scene in [s for s in ct.nodes('Scenes') if any(s.links(label='Treatment'))]: 
    filepath = next(scene.links(label='Treatment')).href
    doc = Document.read_file(filepath)
    print(doc.metadata['synopsis'])
    # doc.metadata['name'] = doc.metadata.get('title', None) or doc.metadata['name'] 
    # synopsis = doc.metadata.get('synopsis', None) or doc.content.strip().replace('\n', ' ')
    # re.sub(r'\"', '', doc.metadata['synopsis'])
     
    # doc.metadata['synopsis'] = "'" + doc.metadata['synopsis'] + "'"
    
    
    #doc.write_file()
    
