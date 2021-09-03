#!/home/jeremy/Python3.6Env/bin/python
# -*- coding: utf-8 -*-
#
#  script.py
#
#  Copyright 2019 Jeremy Allan <jeremy@jeremyallan.com>

"""
Panflute filter to allow file includes

Each include statement has its own line and has the syntax:

    $include ../somefolder/somefile

Each include statement must be in its own paragraph. That is, in its own line
and separated by blank lines.

If no extension was given, ".md" is assumed.

def get_timestamp(node):

    try:
        return next(filter(None, (dateparser.parse(b) for b in node.bullets)))
    except StopIteration:
        print(f'{node.name} has no timestamp')
        raise

def make_slugline(cts, pts):
    data = dict(date=cts.strftime("%B %Y"))
    if not pts:
        data['new'] = True
    elif cts < pts:
        data['flashback'] = True
    elif cts > pts:
        data['return'] = True
    else:
        data['continue'] = True
    return data

"""

import panflute as pf
from pathlib import Path
from collections import defaultdict

def prepare(doc):
    doc.current_header = None
    doc.sections = defaultdict(list)


def action(elem, doc):
    if isinstance(elem, pf.Header) and elem.level == 1:
        doc.current_header = elem.text
    elif isinstance(elem, pf.Para):
        doc.sections[doc.current_header].append(elem)

def finalize(doc):
    header = doc.metadata['header']
    if header and header in doc.sections:
        content = doc.sections['header']
    else:
        content = doc.content
    return content

def main(doc=None):
    return pf.run_filter(action, prepare=prepare, finalize=finalize, doc=doc)


if __name__ == '__main__':
    main()
