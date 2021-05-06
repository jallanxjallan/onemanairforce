from storage.cherrytree import CherryTree, Text, Link
from utility.config import load_config
from utility.strings import snake_case
from pathlib import Path
from document.pandoc import PandocArgs, interfile, stream_pandoc
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

def export_episode(episode):
    story_timestamp = None
    previous_timestamp = None
    pandoc_args = [PandocArgs(input=interfile(),
                                output=interfile(),
                                metadata=dict(episode=episode),
                                template='synopsis')]

    ct = CherryTree('content_index.ctd')
    for chunk in [c for s in ct.nodes(episode) if s.level == 3]:

        for chunk in sequence.parse_content:
            if isinstance(chunk, Text):
                text = str(chunk)
                if len(text.strip()) < 10:
                    continue
                story_content = str(chunk)
                story_timestamp = sequence_timestamp
            elif isinstance(chunk, Link):
                story_node = ct.find_node_by_id(chunk.href)
                if not story_node:
                    continue
                story_content = story_node.content
                story_timestamp = get_timestamp(story_node)
            else:
                continue

            slugline = make_slugline(story_timestamp, previous_timestamp)
            previous_timestamp = story_timestamp

            pandoc_args.append(PandocArgs(input=interfile(story_content),
                                           output=interfile(),
                                           variables=slugline,
                                           template='synopsis'
                          ))

    pandoc_args.append(PandocArgs(inputs=[a.output for a in pandoc_args],
                                  output=output_path.joinpath(snake_case(episode)).with_suffix('.md')))

    stream_pandoc(pandoc_args)

if __name__ == '__main__':
    fire.Fire(export_episode)
