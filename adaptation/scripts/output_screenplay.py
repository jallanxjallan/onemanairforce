#!/home/jeremy/Python3.7Env/bin/python
# coding: utf-8

from pathlib import Path
from collections import defaultdict
from document.document import Document
from document.pandoc import PandocArgs, run_pandoc
from storage.cherrytree import CherryTree
from utility.strings import snake_case
from utility.config import load_config
import fire

def output_book(index_file, output_file):
    ct = CherryTree(index_file)
    sequences = defaultdict(list)
    [sequences[p.parent.name].append(p) for for p in ct.nodes() if p.document_link]
    args = []
    for sequence_no, sequence in enumerate(sequences):
        args.append(PandocArgs(metadata=sequence_no=sequence_no,
                               sequence=sequence
                               defaults='sequence'))
        for scene in sequences[sequence]:
                doc = Document.read_file(scene.document_link)
                args.append(PandocArgs(
                    input=scene.document_link,
                    metadata=doc.metadata,
                    defaults='scene'
                ))
        args.append(PandocArgs(inputs=[a for a in args],
                               output=outputfile,
                               defaults='treatment'
        rs = run_pandoc(args)
        print(rs)

if __name__ == '__main__':
    fire.Fire(output_book)
