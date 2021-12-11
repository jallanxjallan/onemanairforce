#!/home/jeremy/Python3.7Env/bin/python
# -*- coding: utf-8 -*-
#
#  script.py
#
#  Copyright 2019 Jeremy Allan <jeremy@jeremyallan.com>

from operator import itemgetter
from pathlib import Path
from document.document import Document
from storage.cherrytree import CherryTree
from scripts.proofreader import Proofer
from document.pandoc import PandocArgs
from IPython.display import Markdown as md
from dateutil.parser import parse as date_parse
import pandas as pd
import fire
import re


def load_document_data(document_link):
    if not Path(str(document_link)).exists():
        print(f'document_link for {node.name} not valid')
        return False
    document = Document.read_file(str(document_link))
    data = dict(
        document_link=str(document_link),
        text=document.content.lstrip('\n')
    )
    for key in ('title', 'category', 'status'):
        data[key] = document.metadata.get(key, None)

    try:
        date = date_parse(document.date)
    except:
        date = None
    finally:
        data['date'] = date
    return data


CATEGORIES = ('Present', 'Past')

INDEX_FILE = 'screenplay.ctd'

class ScreenplayData():

    def __init__(self):
        ct=CherryTree(INDEX_FILE)
        stories = [n
                   for c in CATEGORIES
                   for n in ct.nodes(c)
                   if n.level > 2
                   if not n.name.startswith("~")]

        scenes = [n for n in ct.nodes('Scenes')]
        story_links = [l for s in scenes for l in s.links if l.type=='node']
        documents = [Document.read_file(s.document_link) for s in scenes if s.document_link]
        df_st = pd.DataFrame([s.asdict('id', 'name') for s in stories]).rename(columns={'id':'story_ref', 'name':'story'})
        df_st['story_sequence'] = df_st.index
        df_sc = pd.DataFrame([s.asdict('id', 'name', 'document_link') for s in scenes]).rename(columns={'id':'scene_ref','name':'scene', 'document_link':'filepath'})
        df_sc['scene_sequence'] = df_sc.index
        df_dot = pd.DataFrame([d.asdict() for d in documents])
        df_dot['filepath'] = df_dot.filepath.apply(lambda x: str(x))

        df_do = pd.concat([df_dot, df_dot["metadata"].apply(pd.Series)], axis=1)
        df_do['date'] = df_do[df_do.date.notna()].date.apply(lambda x: date_parse(x))
        # df_scenes = df_sc.merge(df_do, how='left', on='filepath')
        df_sl = pd.DataFrame([dict(story_ref=l.href, scene_ref=s.id) for s in scenes for l in s.links if l.type=='node'])

        self.df = df_st.merge(df_sl, how='left', on='story_ref')\
                        .merge(df_sc, how='left', on='scene_ref')\
                        .merge(df_do, how='left', on='filepath')
        # self.df = df_scenes


    def show_df(self):
        print(self.df[['scene', 'date', 'filepath']])

    def filter_stories(self, **kwargs):
        """returns subset filtered by sequence, level, category, story, scene regex patterns"""
        clauses = [getattr(ScreenplayData, f)(a) for f,a in kwargs.items()]
        query = ' & '.join([f'({c})' for c in clauses])
        self.df = self.df.dropna(subset=kwargs).query(query)
        return self

    def content(self, arg):
        return f'text.str.contains("{arg}")'

    def category(self, arg):
        return f'category.str.contains("{arg}")'

    def level(self, arg):
        return f'level == {arg}'

    def story(arg):
        return f'story.str.contains("{arg}")'

    def scene(arg):
        return f'scene.str.contains("{arg}")'

    def unplaced_(self, arg):
        self.df = self.df.query('scene.isna()')

    def date_range(self, *bounds):
        min_date = date_parse(bounds.pop[0])
        max_date = date_parse(bounds[0]) if len(
            bounds) > 0 else date_parser('1 January 1990')
        query = 'min_date <= date <= max_date'
        self.df = self.df.dropna(subset=['date']).query(query)

    @property
    def display_scenes(self):
        return self.df.sort_values(['scene_sequence', 'story_sequence'])[['story', 'scene', 'date']]

    @property
    def display_content(self):
        for r in self.df.dropna(subset=['content']).sort_values(['scene_sequence', 'story_sequence']).itertuples():
            try:
                display(
                    md(f'**{r.scene} - {r.date.strftime("%B %Y")}** :  {r.content.lstrip()}'))
            except Exception as e:
                print(f'Cannot display {r.scene} because {e}')

def output_screenplay(outputfile, synopsis=True):
    ct = CherryTree(INDEX_FILE)
    rkey = RedisKey(namespace='omaf', component='slugline.data')

    for node in [n for n in ct.nodes('Scenes') if any(n.links(type='file'))]:
        try:
            previous_sibling_key = str(
                rkey(node.previous_sibling.id))
        except AttributeError:
            previous_sibling_key = str(rkey(0))

        data = dict(
            previous_sibling_key=previous_sibling_key,
            parent_key=str(rkey(node.parent.id)),
            level=node.level,
            name=node.name,
            id=node.id
        )
        scene_key = str(rkey(node.id))
        [rds.hset(scene_key, k,v) for k,v in data.items()]
        rds.expire(scene_key, 120)
        print(PandocArgs(input=next(node.links(type='file')).href,
                         metadata=dict(slugline_data_key=scene_key,

                         filters=['split_on_rule.lua',
                         'insert_slugline.lua',
                         'print_output_file.lua'])))
        if i > 2:
            pass

if __name__ == '__main__':
    fire.Fire(ScreenplayData)

'''
def output_treatment(self, output_file):

'''
