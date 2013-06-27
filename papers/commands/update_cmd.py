from .. import repo
from .. import color

def parser(subparsers, config):
    parser = subparsers.add_parser('update', help='update the repository to the lastest format')
    return parser


def command(config, ui):
    rp = repo.Repository.from_directory(config)
    msg = ("You should backup the paper directory {} before continuing."
           "Continue ?").format(color.dye(rp.papersdir, color.filepath))
    sure = ui.input_yn(question=msg, default='n')
    if sure:
        for p in rp.all_papers():
            tags = set(p.metadata['tags'])
            tags = tags.union(p.metadata['labels'])
            p.metadata.pop('labels', [])
            rp.save_paper(p)
