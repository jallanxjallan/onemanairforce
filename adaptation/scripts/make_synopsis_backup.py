from storage.cherrytree import CherryTree
from utility.config import load_config
from utility.strings import snake_case
from pathlib import Path
from document.pandoc import PandocArgs, interfile, write_pandoc, stream_pandoc
from document.document import Document
import dateparser
import re
import json
import fire
import attr

@attr.s
class Scene():
    sequence = attr.ib()
    timestamp = attr.ib(converter=dateparser)
    synopsis = attr.ib()

    @classmethod
    def load_scene(cls, sequence, link, ct):
        node = ct.find_node_by_id(link.href)
        document = Document.read_file(node.filepath)
        return cls(node.sequence, document.date, document.content)


def format_synopsis(scn, pscn):

    date_diff = scn.delta(pscn)

    

    data = dict(date=scn.timestamp.strftime())


    if not pscn.sequence == scn.sequence:
        data['new'] = True
    elif scn.timestamp < pscn.timestamp:
        data['flashback'] = True
    elif scn.timestamp > pscn.timestamp and 'Interviews' in [a.name for a in scn.node.ancestors]:
        data['return'] = True
    else:
        data['continue'] = True
    return data

def export_episode(episode):
    ct = CherryTree('content_index.ctd')
    output_path = Path('output')
    base_node = ct.find_node_by_name(episode)
    if not base_node:
        pass
        # print(episode, 'not found')
        return False
    pandoc_args = [PandocArgs(input=interfile(),
                                output=interfile(),
                                metadata=dict(episode=episode),
                                template='synopsis')]


    for sequence in base_node.children:
        prev_scene = None
        for link in sequence.links:
            try:
                scene = Scene.load_scene(sequence, link, ct)
            except Exception as e:
                # print(e)
                continue

            pandoc_args.append(PandocArgs(input=interfile(scene.synopsis),
                                        output=interfile(),
                                        # variables=make_slugline(scene, prev_scene, document),
                                        template='synopsis'))
            prev_scene = scene

    pandoc_args.append(PandocArgs(inputs=[a.output for a in pandoc_args],
                                  output=output_path.joinpath(snake_case(episode)).with_suffix('.md')))

    stream_pandoc(pandoc_args)


if __name__ == "__main__":
    fire.Fire(export_episode)
