#!/home/jeremy/Python3.6Env/bin/python
# -*- coding: utf-8 -*-
#
#  script.py
#
#  Copyright 2019 Jeremy Allan <jeremy@jeremyallan.com>

"""
Pandoc filter using panflute
"""

import panflute as pf

def prepare(doc):
    doc.code_blocks = []


def action(elem, doc):
    if isinstance(elem, pf.CodeBlock):
        # doc.code_blocks.append(pf.Header(pf.Str(elem.classes[0]), level=1))
        doc.code_blocks.append(elem)

def finalize(doc):
    doc.content = pf.convert_text('\n'.join(b.text for b in doc.code_blocks))

def main(doc=None):
    return pf.run_filter(action,
                         prepare=prepare,
                         finalize=finalize,
                         doc=doc)

if __name__ == '__main__':
    main()
