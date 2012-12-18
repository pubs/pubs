from .. import repo


def parser(subparsers, config):
    parser = subparsers.add_parser('add_library',
            help='add a set of papers to the repository')
    parser.add_argument('bibfile', help='bibtex, bibtexml or bibyaml file')
    return parser

def command(config, bibfile):
    """
    :param bibtex       bibtex file (in .bib, .bibml or .yaml format.
    """
    rp = repo.Repository.from_directory()
    rp.add_papers(bibfile)
