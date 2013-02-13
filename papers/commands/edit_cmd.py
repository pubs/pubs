import subprocess

from ..color import colored
from .. import repo


def parser(subparsers, config):
    parser = subparsers.add_parser('edit',
            help=colored('open the paper bibliographic file in an editor',
                'normal'))
    parser.add_argument('reference',
            help=colored('reference to the paper (citekey or number)',
                'normal'))
    return parser


def command(config, ui, reference):
    rp = repo.Repository.from_directory()
    key = rp.citekey_from_ref(reference, fatal=True)
    filepath = rp.path_to_paper_file(key, 'bib')
    subprocess.call([config.get('papers', 'edit-cmd'),
        filepath])
    # TODO use editor_input from files.py instead of directly editing the file.
    # Then chack that output file is correctly formmatted and that citekey has
    # not changed or is still a valid citekey.
    print('{} editing {}.'.format(
        colored('Done', 'ok'),
        colored(filepath, 'filepath')
        ))
