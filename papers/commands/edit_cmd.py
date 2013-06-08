from ..files import editor_input
from .. import repo
from ..paper import get_bibentry_from_string, get_safe_metadata_from_content
from .. import configs


def parser(subparsers, config):
    parser = subparsers.add_parser('edit',
            help='open the paper bibliographic file in an editor')
    parser.add_argument('reference',
            help='reference to the paper (citekey or number)')
    parser.add_argument('-m', '--meta', action='store_true', default=False,
            help='edit metadata')
    return parser


def command(config, ui, reference, meta):
    rp = repo.Repository.from_directory(config)
    key = rp.citekey_from_ref(reference, fatal=True)
    paper = rp.paper_from_citekey(key)
    to_edit = 'bib'
    if meta:
        to_edit = 'meta'
    filepath = rp.path_to_paper_file(key, to_edit)
    editor = config.get(configs.MAIN_SECTION, 'edit-cmd')
    with open(filepath) as f:
        content = f.read()
    while True:
        # Get new content from user
        content = editor_input(editor, content)
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
            rp.update(paper, old_citekey=key)
            break
        except repo.CiteKeyAlreadyExists:
            options = ['overwrite', 'edit again', 'abort']
            choice = options[ui.input_choice(
                        options,
                        ['o', 'e', 'a'],
                        question='A paper already exist with this citekey.'
                        )]
            if choice == 'abort':
                break
            elif choice == 'overwrite':
                rp.update(paper, old_citekey=key, overwrite=True)
            # else edit again
