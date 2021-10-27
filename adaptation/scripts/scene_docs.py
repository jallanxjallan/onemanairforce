    from document.document import Document
    from pathlib import Path
    from storage.cherrytree import CherryTree 
    import spacy 
    from spacy.language import Language
    from spacy.tokens import Span
    import pandas as pd 
    import re
    from utility.strings import snake_case
    from utility.config import load_config

    nlp = spacy.load('en_core_web_md')

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
    patterns = [
        {'id':'fado',"label": "GENRE", "pattern": [{"LOWER": 'fado'}, {'LOWER': {'REGEX': '(saudade|despedida|ballada)'}}]},
        {'id':'fado', "label": "GENRE", "pattern": [{"LOWER": "fado"}]},
        {'id':'kr', "label": "SONG",  "pattern": [{"LOWER": {'REGEX': '(cr|kr)'}}, {'TEXT': '.'}]},
    ]
    ruler.add_patterns(patterns)

    @Language.component("keroncong_song_title")
    def kr_song(doc):
        new_ents = []
        for ent in doc.ents:
            if ent.ent_id_ == 'kr': 
                offset = 0
                for i in range(1, 4):
                    offset = i
                    if not doc[ent.end + offset].text.istitle():
                        break 
                new_ents.append(Span(doc, ent.start, ent.end + offset, label='KERONCONG_SONG'))
            else:
                new_ents.append(ent) 
        try:
            doc.ents = new_ents 
        except ValueError:
            pass
            
        return doc

    @Language.component("historical_timeline")
    def timeline(doc):
        new_ents = []
        for ent in doc.ents:
            if ent.label_ == 'DATE' and re.search('(1|2)\d{3}', ent.text):
                new_ents.append(Span(doc, ent.start, ent.end, label='TIMELINE')) 
            else:
                new_ents.append(ent) 
        doc.ents = new_ents 
        return doc

      

    def load_ner(sources):
        nlp = spacy.load('en_core_web_md')
        nlp.disable_pipe("parser")
        nlp.enable_pipe("senter")
        nlp.disable_pipe('ner')
        ner_config = {
           "phrase_matcher_attr": None,
           "validate": True,
           "overwrite_ents": False,
           "ent_id_sep": "||"
        }


        patterns = [
            {'id':'fado',"label": "GENRE", "pattern": [{"LOWER": 'fado'}, {'LOWER': {'REGEX': '(saudade|despedida|ballada)'}}]},
            {'id':'fado', "label": "GENRE", "pattern": [{"LOWER": "fado"}]},
            {'id':'kr', "label": "SONG",  "pattern": [{"LOWER": 'kr'}, {"IS_PUNCT": True}]},
            {'id':'kr', "label": "SONG",  "pattern": [{"LOWER": 'cr'}, {"IS_PUNCT": True}]}
        ]
        
        ruler = nlp.add_pipe("entity_ruler", config=ner_config, before='ner')
        nlp.add_pipe("keroncong_song_title", after="ner") 
        nlp.add_pipe("historical_timeline", after="ner") 
        ruler.add_patterns(patterns) 
        docs = nlp.pipe([(r.content, r.id) for r in sources.itertuples()], as_tuples=True)
        return pd.DataFrame([
            dict(text=e.text, 
                  label=e.label_, 
                  sent=e.sent,
                  ent_id=e.ent_id_, 
                  doc_id=id
            )  
              for d, id in docs for e in d.ents])
            

    def doc_data(node):
        try:
            doc = Document.read_file(node.document_link) 
        except: 
            print('unable to parse', node.document_link) 
            return {}
        return dict(id=node.id,
                    chapter=node.parent.name, 
                    scene=node.name, 
                    status=doc.status, 
                    wordcount=doc.wordcount,
                   content=doc.content)

    ct = CherryTree('book')
    df = pd.DataFrame([doc_data(n) for n in ct.nodes() if n.document_link])

    df_ents = load_ner(df)
    df_ents[df_ents.ent_id == 'kr' ].text.unique()

    df_ents[df_ents.text.str.contains('Guido', case=False)].sort_values('text').tail(50)

    df[df.id=='137']

    df['wordcount'] = df.doc.apply(lambda d: len([t for t in d if not t.is_punct]))

    df[df.status == 'draft'].wordcount.sum()


    # docs = load_docs('book', 'Multilingual Repertoire')
        
    df_ents = pd.DataFrame([dict(filepath=d.filepath, 
                            id=e.ent_id_, 
                            start=e.start, 
                            end=e.end, 
                            label=e.label_,
                            sent=e.sent,
                            entity=e.text) for d in df.itertuples() for e in d.doc.ents]) 

    df_ents.to_pickle('source_entities.pkl')

    dfents.head()

    book_args = []
    ct = CherryTree('book.ctd') 
    for chapter in [n for n in ct.nodes() if n.level == 1]:
        chapter_args = dict(metadata=dict(chapter_no=chapter.sequence +1, chapter=chapter.name), template='chapter')
        scene_args = [PandocArgs(input=s.document_link) for s in chapter.children if s.document_link]
        if not scene_args: 
            chapter_args['text'] = 'Content to come'
        
        book_args.append(PandocArgs(**chapter_args))
        book_args.extend(scene_args)
    book_args.append(PandocArgs(inputs=book_args, output='output/test_chapter_output.docx', metadata=dict(title='Keroncong'))) 
    run_pandoc(book_args)

    grp = df.groupby('chapter', sort=False).agg({'wordcount': sum}) 
    for g in grp.itertuples(): print(g.Index, g.wordcount)

    df.wordcount.sum()

    ct = CherryTree('book')
    df = pd.DataFrame([doc_data(n) for n in ct.nodes() if n.document_link])
    df[['scene', 'status']]

    cs = [t for t in doc.noun_chunks]

    g = cs[2] 
    g.label_

    dfe = pd.read_pickle('ents.pkl')

    dfs = dfe[dfe.filepath.str.startswith('source')]

    a = dfs[dfs.label == 'NORP'].entity.sort_values().unique()
    Path('ethnic_groups.txt').write_text('\n'.join(a))

    ethnics = np.loadtxt('ethnic_groups.txt', dtype=str, delimiter='\n')

    terms = '|'.join(('Mardijkers',))
    dfs[dfs.entity.str.contains(terms)].filepath.unique()

    ct = CherryTree('book.ctd')
    [n.name for n in ct.nodes() if n.level == 3 if not n.document_link]

    docs = load_docs('book')

    for no, ent in enumerate([e for d in docs for e in d[0].ents]):
        key = f'keroncong:labels:{no}'
        rds.hset(key, ent.text, ent.label_)
        rds.hset('keroncong:labels:index', ent.text, key)

    pd.DataFrame([dict(a='b', c='d')]).to_pickle('in_a_pickle.pkl')

    n.level

    n.parent

    for node in [n for  n in ct.nodes() if n.level==1]:
        t = node.element.getroottree()
        r = t.getroot()
        i = r.index(node.element)
        print(i, node.name)

    ct = CherryTree('book.ctd')
    doc_links = set(n.document_link for n in ct.nodes() if n.document_link) 
    filepaths = set(str(f) for f in Path('edits').iterdir() if f.suffix == '.md') 
    filepaths.difference(doc_links)

    ct = CherryTree('book.ctd')

    for node in [n for n in ct.nodes() if n.document_link]:
        node_name = snake_case(node.name)
        file_name = Path(node.document_link)
        if not node_name == file_name.stem:
            print(node.name, node.document_link) 
    #         new_name = file_name.with_name(f'{node_name}.md')
    #         file_name.rename(new_name)
            

    index_key = 'victor:document:index'
    df_sources = pd.DataFrame(nlp.pipe([(rds.hget(k, 'content'), Path(f).stem) 
                            for f,k in rds.hgetall(index_key).items()], as_tuples=True), columns=['doc', 'source'])
        

    df_sources[df_sources.source.str.contains('98')].doc

    df_sources = pd.read_pickle('sources.pkl')
    # df_sources.iloc[2:3].doc.to_clipboard()

    df[df.content.str.contains('Manuel Godinho de Eredia')]

    sources.rename(columns=dict(raw='content'), inplace=True)

    df_sources['content'] = df_sources.doc.apply(lambda x: str(x))

    df_sources[df_sources.content.str.contains('Ujung Kulon')]

    df_sources.iloc[32].name

    from spacy.matcher import Matcher
    matcher = Matcher(nlp.vocab)

    patterns = load_config('match_patterns')
        
        
    #     'TuguMoresco':[{'ENT_TYPE': 'DATE'}, {'TEXT': {'REGEX':'19[1-3]\d'}}]}

    for label, pats in patterns.items():
        matcher.add(label, [[p for p in pats]] if len(pats) > 1 else [[pats]])



    def match_term(d):
        matches = matcher(d.doc)
        
        for match_id, start, end in matches:
            rds.setnx(f'keroncong:search:{d.name}', str(d.doc))
        

    df_sources.apply(lambda x: match_term(x), axis=1)

    df_sources.iloc[57].doc

    pages = '15|17|18|84|90|98|99'
    df_croc = df_sources[df_sources.source.str.contains(pages)]
    df_croc.doc.values[0]

    for para in Para.select(lambda c: c.doc_file.name == 'book'):
        print(para.text)
        print('-' * 10)

    docs = nlp.pipe([p.text for p in Para.select()])

    # sqlite_connection = connect('sources.db')
    df_source_ents = pd.read_sql_table('entity', 'sqlite:///sources.db')

    pd.DataFrame([dict(label=e.label_, entity=e.text) for d in docs for e in d.ents]).drop_duplicates().to_sql('entities', sqlite_connection)

    label = 'ORG'
    edit_ents = df_ents[df_ents.label == label]
    source_ents = df_source_ents[df_source_ents.label == label]
    source_ents[~source_ents.text.isin(edit_ents.text)].head(50)

    ct = CherryTree('book')
    [n.name for n in ct.nodes() if n.level == 2 if not n.document_link]

    ['Rise of Natinalism', 'Pacific War', 'Struggle for Independence']

    docs = nlp.pipe([Document.read_file(f).content for f in Path('edits').iterdir()])

    df = pd.DataFrame([e.text for d in docs for e in d.ents if e.label_ in  ('PERSON', 'ORG')], columns=['name'])

    df.drop_duplicates().tail(50)

                                     name
    1402         Molaccans Chris Sahetapi
    1403                Leo Sapulete Bram
    1404    the Fandel Krontjong Concours
    1405                    Gambir Market
    1406                         Abdullah
    1409                        Jong Java
    1410                          Dobbert
    1412              the Gezang Concours
    1413                   Master's Voice
    1414                      Bram Aceh's
    1415                          Hoegeng
    1417          Jakarta Central Station
    1418                Kerontjong Toegoe
    1419                           Joseph
    1420                    Bernard Quiko
    1422                    Theo Abrahams
    1424                      Eddy Waasch
    1425                       Piet Klaas
    1426                    Oma Christine
    1428              Krontjong Toegoe\'s
    1433                 Portugis Cristão
    1434                      Tugu Betawi
    1435        Cafrinho                1
    1436         Moresco                2
    1437  Schoon ver van jou            2
    1439         Prounga                3
    1444                     Mato        
    1445                Mijn Sarie Mareis
    1447              B.O.S.           \n
    1448                   Pantai Marunda
    1449                         Bastiana
    1450           Nina Bobo            8
    1451   Lieve Sonja                   
    1452                        Jali-jali
    1453               Macau Sa Assi     
    1454                     Daar Bij die
    1455               Molen            9
    1456         Sarinah Kind uit de Desa
    1458  De Sterren                   11
    1459                       Als de zon
    1460                    Westen Nedert
    1461                     Terang Bulan
    1462            Bloeien            13
    1463    Lang zal ze Leven            
    1464                      Jalan Bunda
    1465                    Slaap Kind je
    1466                     Tanah Toegoe
    1469         De Mardijkers       \n\n
    1471                         Manusama
    1480           the Dutch East\nIndies
