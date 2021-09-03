from storage.cherrytree import CherryTree, Text, Link
from utility.config import load_config
from utility.strings import snake_case
from pathlib import Path
from document.pandoc import PandocArgs, run_pandoc
import dateparser
import attr
import fire
from tempfile import TemporaryDirectory

output_path = Path('output')


def export_synopsis(outfile):
    story_timestamp = None
    previous_timestamp = None
    pandoc_args = []

    ct = CherryTree('content_index.ctd')
    base_node = ct.find_node_by_name('Synopsis')
    episode_files = []
    with TemporaryDirectory as tdir:
        for episode in base_node.children:
            pandoc_args.append(PandocArgs(
                                      metadata=dict(episode=episode.name),
                                      template='synopsis'
                                      ))

            sequence_args = []
            for sequence in episode.children:
                for seq, link in enumerate([l for l in sequence.links if l.type == 'file']):
                    sequence_args.append(PandocArgs(input=link.href,
                                                filters=['format_scene.py'],
                                                metadata=dict(seq=seq, header=link.text),
                                                template='synopsis'))
                    episode_files.append(run_pandoc(sequence_args))
        

    rs = run_compiled(pandoc_args, output=outfile, debug=True)
    print(rs)

if __name__ == '__main__':
    fire.Fire(export_synopsis)
