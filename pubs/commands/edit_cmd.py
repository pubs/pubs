from ..content import editor_input
from .. import repo
from ..paper import get_bibentry_from_string, get_safe_metadata_from_content
from ..configs import config
from ..uis import get_ui


def parser(subparsers):
    parser = subparsers.add_parser('edit',
            help='open the paper bibliographic file in an editor')
    parser.add_argument('-m', '--meta', action='store_true', default=False,
            help='edit metadata')
    parser.add_argument('citekey',
            help='citekey of the paper')
    return parser


def edit_meta(citekey):
    rp = repo.Repository(config())
    coder = endecoder.EnDecoder()
    filepath = os.path.join(rp.databroker.databroker.filebroker.metadir(), citekey+'.yaml')
    with open(filepath) as f:
        content = f.read()



def edit_bib(citekey):
    rp = repo.Repository(config())
    coder = endecoder.EnDecoder()
    filepath = os.path.join(rp.databroker.databroker.filebroker.bibdir(), citekey+'.bib')
    with open(filepath) as f:
        content = f.read()



def command(args):

    ui = get_ui()
    meta = args.meta
    citekey = args.citekey

    rp = repo.Repository(config())
    coder = endecoder.EnDecoder()
    if meta:
        filepath = os.path.join(rp.databroker.databroker.filebroker.metadir(), citekey+'.yaml')
    else:
        filepath = os.path.join(rp.databroker.databroker.filebroker.bibdir(), citekey+'.bib')

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
                        question='A paper already exists with this citekey.'
                        )]

            if choice == 'abort':
                break
            elif choice == 'overwrite':
                paper = rp.save_paper(paper, old_citekey=key, overwrite=True)
                break
            # else edit again
