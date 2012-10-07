from .. import color
from .. import files

try:
    import ConfigParser as configparser
except ImportError:
    import configparser



def parser(subparsers, config):
    parser = subparsers.add_parser('add', help='add a paper to the repository')
    parser.add_argument('pdffile', help='pdf or ps file')
    parser.add_argument('bibfile', help='bibtex, bibtexml or bibyaml file')
    return parser


def command(config, pdffile, bibfile):
    """
    :param pdffilepath  path (no url yet) to a pdf or ps file
    :param bibtex       bibtex file (in .bib, .bibml or .yaml format.
    """
    papersdir = files.find_papersdir()

    fullpdfpath = os.path.abspath(pdffile)
    fullbibpath = os.path.abspath(bibtex)
    files.check_file(fullpdfpath)
    files.check_file(fullbibpath)

    filename, ext = os.path.splitext(os.path.split(fullpdfpath)[1])
    if ext != '.pdf' and ext != '.ps':
        print('{}warning{}: extention {}{}{} not recognized{}'.format(
               color.yellow, color.grey, color.cyan, ext, color.grey, color.end))

    meta = configparser.ConfigParser()
    meta.add_section('metadata')

    meta.set('metadata', 'filename', filename)
    meta.set('metadata', 'extension', ext)
    meta.set('metadata', 'path', os.path.normpath(fullpdfpath))

    meta.add_section('notes')

    if bibtex is not None:
        bib_data = files.load_externalbibfile(fullbibpath)
        print('{}bibliographic data present in {}{}{}'.format(
               color.grey, color.cyan, bibtex, color.end))
        print(bib_desc(bib_data))
        files.write_bibfile(bib_data, filename)

    papers = files.read_papers()
    count = papers.get('header', 'count')
    papers.set('header', 'count', int(count) + 1)
    papers.set('papers', 'p' + count, filename)

    files.write_papers(papers)
    files.write_meta(meta, filename)
