#!/home/jeremy/Python3.7Env/bin/python
# -*- coding: utf-8 -*-
#
#  script.py
#
#  Copyright 2019 Jeremy Allan <jeremy@jeremyallan.com>

import sys
from pathlib import Path
import fire
from storage.cherrytree import CherryTree
from document.document import Document
from utility.strings import snake_case, title_case
import peewee as pw
from playhouse.sqlite_ext import *

db = pw.SqliteDatabase('document_archive.db')

class DocumentArc(pw.Model):
    section = pw.CharField(null=True)
    name = pw.CharField()
    content = pw.CharField(null=True, unique=True)
    meta = JSONField(null=True)

    class Meta:
        database = db # This model uses the "people.db" database.

def archive_index(index_file):
    ct = CherryTree(index_file)
    index_data = []
    for node in ct.nodes():
        try:
            section = [a.name for a in node.ancestors][0]
        except IndexError:
            continue
        index_data.append(dict(section=section,
                         name=node.name,
                         notes=node.notes + node.content))
                         
    return index_data


def archive_content():
    archive_folder = Path('archive')
    folders = ['scenes_archive', 'synopsis_archive']
    data = []
    db.create_tables([DocumentArc])
    for index_file in [f for f in archive_folder.iterdir() if f.suffix == '.ctd']:
        data.extend(archive_index(index_file))
    for filepath in [fp for fl in folders for fp in archive_folder.joinpath(fl).iterdir()]:
        doc = Document.read_file(filepath)

        data.append(dict(
                     name=title_case(filepath.stem),
                     content=doc.content,
                     meta = doc.metadata
                     ))

    with db.atomic():
        DocumentArc.insert_many(data).execute()


    for record in DocumentArc.select():
        print(record.name)
if __name__ == '__main__':
    fire.Fire(archive_content)
