#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import sys
from pathlib import Path
from collections import defaultdict
import attr
import fire
import dateparser
from tempfile import mkdtemp
from lxml import etree

sys.path.append('/home/jeremy/Library')
from editing.document_index import DocumentIndex
from document.yaml_document import load_yaml_from_file, dump_yaml_to_file
from utility.helpers import make_identifier, title_case, snake_case
import roman


compile_dir = Path(mkdtemp())
blank_file = 'blank_file.md'

@attr.s
class Defaults():
    defaults = attr.ib(converter=load_yaml_from_file)
    metadata = attr.ib(default=None)
    input = attr.ib(default=None)
    output = attr.ib(default=None)
    filepath = attr.ib()
    @filepath.default
    def _random_filepath(self):
         return str(compile_dir.joinpath(make_identifier()).with_suffix('.yaml'))

    def __attrs_post_init__(self):
        if self.metadata:
            if 'metadata' in self.defaults:
                self.defaults['metadata'].update(self.metadata)
            else:
                self.defaults['metadata'] = self.metadata
        if self.input and type(self.input) is list:
            self.defaults['input-files'] = self.input

        elif self.input and type(self.input) is str:
            self.defaults['input-file'] = self.input
        else:
            self.defaults['input-file'] = blank_file

        if self.output:
            self.defaults['output-file'] = self.output
        else:
            self.output = str(compile_dir.joinpath(make_identifier()).with_suffix('.md'))
            self.defaults['output-file'] = self.output

    def save(self):
        try:
            dump_yaml_to_file(self.defaults, self.filepath)
        except Exception as e:
            print(e)
            return None
        return self.filepath

def make_anchor(anchor, entry, text, base_node, output_dir):
    name = anchor.name
    pos = int(anchor.element.attrib['char_offset'])
    try:
        item = text[pos:-1].split('\n')[0]
    except TypeError:
        return False
    identifier=make_identifier()
    metadata = dict(
        identifier=identifier,
        title=title_case(name),
        parent=entry.name,
        component=base_node
    )
    input_file=compile_dir.joinpath(identifier).with_suffix('.md')
    input_file.write_text(item)
    output_file = output_dir.joinpath(f'{snake_case(base_node)}_{snake_case(name)}').with_suffix('.md')
    defaults = Defaults('note.yaml',
        input=str(input_file),
        output=str(output_file),
        metadata=metadata
    )
    print(defaults.save())


def extract_notes(index_file, output_dir, base_node=None):


    idx = DocumentIndex(index_file)
    output_dir = Path(output_dir)

    for entry in idx.entries(base_node):
        try:
            parent = entry.parent.name
        except AttributeError:
            parent = 'Orphan'
        text = ' '.join([e for e in entry.texts])
        anchors = [a for a in entry.anchors]
        if len(anchors) > 0:
            for anchor in anchors:
                make_anchor(anchor, entry, text, base_node, output_dir)
        else:
            identifier=make_identifier()
            metadata = dict(
                identifier=identifier,
                title=entry.name,
                parent=parent,
                component=base_node
            )
            input_file=compile_dir.joinpath(identifier).with_suffix('.md')
            input_file.write_text(text)
            output_file = output_dir.joinpath(f'{snake_case(base_node)}_{snake_case(entry.name)}').with_suffix('.md')
            defaults = Defaults('note.yaml',
                input=str(input_file),
                output=str(output_file),
                metadata=metadata
            )
            print(defaults.save())









        # if entry.filepath:
        #     dfs = Defaults('passage.yaml', input=entry.filepath)
        # elif entry.level == 1:
        #     parts += 1
        #     metadata = dict(
        #                     component='Part',
        #                     seq=roman.toRoman(parts)
        #                     )
        #     dfs = Defaults('part.yaml', metadata=metadata)
        # elif entry.level == 2:
        #     chapters += 1
        #     metadata =  dict(title=entry.name,
        #                      subtitle=timeline_entry(entry, periods),
        #                      component='Chapter',
        #                      seq=chapters
        #                      )
        #     dfs = Defaults('chapter.yaml', metadata=metadata)
        #
        # print(dfs.save())

if __name__ == '__main__':
    fire.Fire(extract_notes)
