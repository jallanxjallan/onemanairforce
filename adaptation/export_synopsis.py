from storage.cherrytree import CherryTree, Text, Link
from utility.config import load_config
from utility.strings import snake_case
from pathlib import Path
from document.pandoc import PandocArgs, run_compiled
import dateparser
import attr
import fire

output_path = Path('output')

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

def export_synopsis(outfile):
    story_timestamp = None
    previous_timestamp = None
    pandoc_args = []

    ct = CherryTree('content_index.ctd')
    for sequence in [s for s in ct.nodes('Synopsis') if s.level == 3]:
        for link in [l for l in sequence.links if l.type == 'file']:
            pandoc_args.append(PandocArgs(input=link.href,
                                           output='temp',
                                           filters=['format_scene.py'],
                                           variables=slugline,
                                           metadata=dict(header=link.text),
                                           template='synopsis'))



    pandoc_args.append(PandocArgs(inputs=[a.output for a in pandoc_args], output=outputfile))

    rs = run_pandoc(pandoc_args)

if __name__ == '__main__':
    fire.Fire(export_synopsis)
