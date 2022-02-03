dfd = pd.DataFrame([dict(doc=Document.read_file(s.document_link)) for s in scene_nodes])
dfd['filepath'] = dfd.doc.apply(lambda x: x.filepath)
dfd['content'] = dfd.doc.apply(lambda x: x.content)
dfd['metadata'] = dfd.doc.apply(lambda x: x.metadata)
dfd = dfd.merge(dfd.metadata.apply(pd.Series), left_index=True, right_index=True)
dfd['datestamp'] = dfd[dfd.date.notna()].date.apply(lambda x: date_parse(x))
dfd.drop(['doc', 'metadata'], axis=1, inplace=True)
