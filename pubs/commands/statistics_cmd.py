from ..repo import Repository
from ..uis import get_ui
from .. import color


def parser(subparsers, conf):
    parser = subparsers.add_parser(
        'statistics',
        help="show statistics on the repository.")
    return parser


def command(conf, args):
    ui = get_ui()
    rp = Repository(conf)
    papers = list(rp.all_papers())

    paper_count = len(papers)
    if paper_count == 0:
        ui.message('Your pubs repository is empty.')

    else:
        doc_count = sum([0 if p.docpath is None else 1 for p in papers])
        tag_count = len(list(rp.get_tags()))
        papers_with_tags = sum([0 if p.tags else 1 for p in papers])

        ui.message(color.dye_out('Repository statistics:', 'bold'))
        ui.message('Total papers: {}, {} ({}) have a document attached'.format(
            color.dye_out('{:d}'.format(paper_count), 'bgreen'),
            color.dye_out('{:d}'.format(doc_count), 'bold'),
            '{:.0f}%'.format(100. * doc_count / paper_count),
        ))
        ui.message('Total tags: {}, {} ({}) of papers have at least one tag'.format(
            color.dye_out('{:d}'.format(tag_count), 'bgreen'),
            color.dye_out('{:d}'.format(papers_with_tags), 'bold'),
            '{:.0f}%'.format(100. * papers_with_tags / paper_count),
        ))
