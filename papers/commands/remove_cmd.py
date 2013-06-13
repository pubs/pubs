from .. import repo
import color

def parser(subparsers, config):
    parser = subparsers.add_parser('remove', help='removes a paper')
    parser.add_argument('reference',
            help='reference to the paper (citekey or number)')
    return parser


def command(config, ui, reference):
    rp = repo.Repository.from_directory(config)
    key = rp.citekey_from_ref(reference, fatal=True)
    paper = rp.paper_from_citekey(key)
    are_you_sure = ("Are you sure you want to delete paper [%s]"
        " (this will also delete associated documents)?"
        % color.dye(paper.citekey, color.citekey))
    sure = ui.input_yn(question=are_you_sure, default='n')
    if sure:
        rp.remove(paper.citekey)
