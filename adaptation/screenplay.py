#!/home/jeremy/Python3.7Env/bin/python
# -*- coding: utf-8 -*-
#
#  script.py
#
#  Copyright 2019 Jeremy Allan <jeremy@jeremyallan.com>

from operator import itemgetter
from pathlib import Path
from document.document import Document
from document.pandoc import PandocArgs

from storage.cherrytree import CherryTree
from storage.redis import rds, RedisKey

from IPython.display import Markdown as md
from dateutil.parser import parse as date_parse
import pandas as pd
import fire
import re

CATEGORIES = ('Present', 'Past')

INDEX_FILE = 'screenplay.ctd'

CT = None


def get_sequence(id):
    node = CT.find_node_by_id(id)
    try:
        return CT.ancestors(node)[1].name
    except IndexError:
        return node.name


def load_incident(node):
    return dict(
        incident_ref=node.id,
        incident=node.name,
        story=CT.parent(node).name
    )


def load_scene(node):
    data = dict(
        scene_ref=node.id,
        scene=node.name)
    try:
        data['sequence'] = CT.parent(node).name
    except:
        pass
    if node.document_link:
        try:
            doc = Document.read_file(node.document_link)
        except:
            print('Cannot load', node.document_link)
        else:
            data['content'] = doc.content
            for k, v in doc.metadata.items():
                data[k] = v
    return data


def load_links(link, scene):
    return dict(incident_ref=link.href, scene_ref=scene.id)


class ScreenplayData():

    def __init__(self):
        global CT
        CT = CherryTree(INDEX_FILE)
        incidents = pd.DataFrame([load_incident(n)
                                  for c in CATEGORIES
                                  for n in CT.nodes(c)
                                  if n.level > 2
                                  if not n.name.startswith("~")])
        incidents['incident_no'] = incidents.index
        scenes = pd.DataFrame([load_scene(n) for n in CT.nodes('Scenes')])
        scenes['scene_no'] = scenes.index
        scenes['date'] = scenes[scenes.date.notna()].date.apply(
            lambda x: date_parse(x))
        scene_links = pd.DataFrame([load_links(l, s)
                                    for s in CT.nodes('Scenes') for l in s.links if l.type == 'node'])

        self.df = incidents.merge(scene_links, how='left', on='incident_ref')\
            .merge(scenes, how='left', on='scene_ref')

    def filter_by_keyword(self, negate=False, **kwargs):
        """returns subset filtered by sequence, category, story, scene regex patterns"""
        prefix = "~" if negate else ""
        clauses = [
            f'({prefix}{f.lower()}.str.contains("{a}"))' for f, a in kwargs.items()]
        query = ' & '.join(clauses)
        self.df = self.df.dropna(subset=kwargs).query(query)
        return self

    def filter_by_existence(self, **kwargs):
        """returns subset filtered by whether field is null or not"""
        clauses = [
            f'({f.lower()}.{"notna()" if a else "isna()"})' for f, a in kwargs.items()]
        query = ' & '.join(clauses)
        self.df = self.df.query(query)
        return self

    def date_range(self, *bounds):
        min_date = date_parse(bounds[0])
        try:
            max_date = date_parse(bounds[1])
        except IndexError:
            max_date = date_parser('1 January 1990')
        tdf = self.df.dropna(subset=['date'])
        self.df = tdf[(min_date <= tdf.date) & (tdf.date <= max_date)]
        return self

    @property
    def display_count(self):
        return self.df.count()

    @property
    def display_outline(self):
        return self.df.sort_values('scene_no')[['sequence', 'story', 'incident', 'scene', 'date', ]]

    @property
    def display_content(self):
        for r in self.df.dropna(subset=['content']).sort_values(['scene_no', 'incident_no']).itertuples():
            try:
                display(
                    md(f'**{r.scene} - {r.date.strftime("%B %Y")}** :  {r.content.lstrip()}'))
            except Exception as e:
                print(f'Cannot display {r.scene} because {e}')


def output_screenplay():
    CT = CherryTree(INDEX_FILE)
    rkey = RedisKey(namespace='omaf', component='slugline.data')

    for i, node in enumerate([n for n in CT.nodes('Scenes') if n.document_link]):
        try:
            previous_sibling_key = str(
                rkey(CT.previous_sibling(node).id))
        except AttributeError:
            previous_sibling_key = str(rkey(1100000))

        data = dict(
            previous_sibling_key=previous_sibling_key,
            parent_key=str(rkey(CT.parent(node).id)),
            level=node.level,
            name=node.name,
            id=node.id
        )
        scene_key = str(rkey(node.id))
        [rds.hset(scene_key, k, v) for k, v in data.items()]
        rds.expire(scene_key, 120)
        print(PandocArgs(input=node.document_link,
                         metadata=dict(slugline_data_key=scene_key),
                         filters=['insert_slugline.lua',
                                  'print_output_file.lua']))
        if i > 20:
            break


if __name__ == '__main__':
    fire.Fire(output_screenplay)

'''
def output_treatment(self, output_file):

'''
