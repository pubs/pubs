from ..files import editor_input
from .. import repo
from ..paper import get_bibentry_from_string, get_safe_metadata_from_content
from .helpers import add_references_argument, parse_reference
from ..configs import config


def parser(subparsers):
    parser = subparsers.add_parser('edit',
            help='open the paper bibliographic file in an editor')
    parser.add_argument('-m', '--meta', action='store_true', default=False,
            help='edit metadata')
    add_references_argument(parser, single=True)
    return parser


def command(args):

    ui = args.ui
    meta = args.meta
    reference = args.reference

    rp = repo.Repository(config())
    key = parse_reference(ui, rp, reference)
    paper = rp.get_paper(key)
    filepath = rp._metafile(key) if meta else rp._bibfile(key)

    with open(filepath) as f:
        content = f.read()

    while True:
        # Get new content from user
        content = editor_input(config().edit_cmd, content)
        new_key = key
        bib = None
        metadata = None
        # Parse new content
        if meta:
            metadata = get_safe_metadata_from_content(content)
        else:
            new_key, bib = get_bibentry_from_string(content)
        paper.update(key=new_key, bib=bib, meta=metadata)

        try:
            paper = rp.save_paper(paper, old_citekey=key)
            break
        except repo.CiteKeyCollision:
            options = ['overwrite', 'edit again', 'abort']
            choice = options[ui.input_choice(
                        options, ['o', 'e', 'a'],
                        question='A paper already exist with this citekey.'
                        )]

            if choice == 'abort':
                break
            elif choice == 'overwrite':
                paper = rp.save_paper(paper, old_citekey=key, overwrite=True)
                break
            # else edit again
