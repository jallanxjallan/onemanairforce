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
for sequence in [s for s in ct.nodes('Scenes') if s.level == 2]:
    synopses = list(filter(None, [get_synopsis(s) for s in ct.descendants(sequence)]))
    intro = get_synopsis(sequence) 
    if intro:
        synopses.insert(0, intro)
    filepath=Path('sequences', snake_case(sequence.name)).with_suffix('.md')
    document = Document(content=synopses, 
                        metadata=dict(title=sequence.name, status='new')) 
    
    # document.write_file(filepath)
    
