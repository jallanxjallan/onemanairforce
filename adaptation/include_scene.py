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
"""

import os
import panflute as pf
from document.document import Document
from pathlib import Path

def action(elem, doc):
    if isinstance(elem, pf.Para) and type(elem.content[0]) == pf.Link:
        link = elem.content[0]
        base_path = Path('synopsis')

        filepath = base_path.joinpath(Path(link.url).name)

        document = Document.read_file(str(filepath))

        return pf.convert_text(document.synopsis)


        # Alternative A:
        # return new_elems
        # Alternative B:
        # div = pf.Div(*new_elems, attributes={'source': fn})
        # return div


def main(doc=None):
    return pf.run_filter(action, doc=doc)


if __name__ == '__main__':
    main()
