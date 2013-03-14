from ..files import editor_input
from .. import repo
from ..paper import get_bibentry_from_string


def parser(subparsers, config):
    parser = subparsers.add_parser('edit',
            help='open the paper bibliographic file in an editor')
    parser.add_argument('reference',
            help='reference to the paper (citekey or number)')
    return parser


def command(config, ui, reference):
    rp = repo.Repository.from_directory()
    key = rp.citekey_from_ref(reference, fatal=True)
    paper = rp.paper_from_citekey(key)
    filepath = rp.path_to_paper_file(key, 'bib')
    editor = config.get('papers', 'edit-cmd')
    with open(filepath) as f:
        content = f.read()
    while True:
        # Get new content from user
        content = editor_input(editor, content)
        # Parse new content
        new_key, bib = get_bibentry_from_string(content)
        paper.update(key=key, bib=bib)
        # TODO merge into an update method
        paper.citekey = new_key
        paper.bibentry = bib
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
