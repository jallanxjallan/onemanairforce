#!/home/jeremy/Python3.6Env/bin/python
# -*- coding: utf-8 -*-
#
#  script.py
#
#  Copyright 2019 Jeremy Allan <jeremy@jeremyallan.com>

import sys
import os
import re
import fire
import attr
from pathlib import Path
import dateparser
import redis


from storage.cherrytree import CherryTree, Link
from document.pandoc import PandocArgs, interfile, run_pandoc
from utility.helpers import snake_case

sys.path.append('/home/jeremy/Scripts')
from update_document_metadata import update_document_metadata

r = redis.Redis(decode_responses=True)

@attr.s
class Slugline():
    cd=attr.ib(default=None)
    cl=attr.ib(default=None)

    def make_slugline(self, filepath):
        if not filepath:
            raise FileNotFoundError (filepath, 'not found')
        fp = Path(filepath) if type(filepath) is str else filepath
        metadata_key = f'document:metadata:{fp.stat().st_ino}'
        date = dateparser.parse(r.hget(metadata_key, 'date'))
        location = r.hget(metadata_key, 'location')
        return dict(prepend=f'{date.strftime("%B %Y")} : {location}')

class Synopsis():
    def __init__(self, index_file):
        update_document_metadata(index_file, 'Scenes')
        self.ct = CherryTree(index_file)
        self.filepaths = []

    def story(self, story):
        self.output_filename = f'story_{snake_case(story)}'
        story_node = self.ct.find_node_by_name(story)
        if not story_node:
            raise AttributeError
        for scene_node in [s for s in self.ct.nodes('Scenes') if s.filepath]:
            for ref_node_id in [l.href for l in scene_node.links if l.type == 'node']:
                ref_node = self.ct.find_node_by_id(ref_node_id)
                if not ref_node:
                    continue
                if story_node.id in [a.id for a in ref_node.ancestors]:
                    self.filepaths.append(scene_node.filepath)
        return self

    def sequence(self, sequence='Scenes'):
        sequence_node = self.ct.find_node_by_name(sequence)
        if not sequence_node:
            raise AttributeError (sequence, 'not found')
        self.output_filename = f'sequence_{snake_case(sequence)}'
        self.filepaths.extend([Path(s.filepath) for s in self.ct.nodes(sequence) if s.filepath])
        return self

    def output(self, target, output_dir='output'):

        fp = Path(output_dir)
        if not fp.exists():
            raise FileNotFoundError

        sl = Slugline()
        args = []
        for filepath in self.filepaths:
            pa = PandocArgs(
                input=filepath,
                output=interfile(),
                filters=['strip_codeblocks.lua']
            )
            try:
                metadata=sl.make_slugline(filepath)
            except Exception as e:
                print(e)
                continue
            if metadata:
                pa.metadata=metadata
                pa.filters.append('prepend_text.lua')

            args.append(pa)

        rs = run_pandoc(args)

        for o in rs.output: print(o)
        for e in rs.errors: print(e)

        filters = None

        if target == 'review':
            suffix = '.md'
        elif target == 'submit':
            suffix = '.docx'
            # filters = [make_slugline]
        else:
            raise AttributeError (target, 'unknown')


        rs = run_pandoc(
            PandocArgs(
                inputs=[i.output for i in args],
                output=fp.joinpath(self.output_filename).with_suffix(suffix)
            ))

        for o in rs.output: print(o)
        for e in rs.errors: print(e)

if __name__ == '__main__':
    fire.Fire(Synopsis)
