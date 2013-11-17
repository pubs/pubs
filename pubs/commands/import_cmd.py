import os
import datetime

from pybtex.database import Entry, BibliographyData, FieldDict, Person

from .. import repo
from .. import endecoder
from .. import bibstruct
from .. import color
from ..paper import Paper
from ..configs import config
from ..uis import get_ui



def parser(subparsers):
    parser = subparsers.add_parser('import',
            help='import paper(s) to the repository')
    parser.add_argument('bibpath',
            help='path to bibtex, bibtexml or bibyaml file (or directory)')
    parser.add_argument('-c', '--copy', action='store_true', default=None,
            help="copy document files into library directory (default)")
    parser.add_argument('-C', '--nocopy', action='store_false', dest='copy',
            help="don't copy document files (opposite of -c)")
    parser.add_argument('keys', nargs='*',
            help="one or several keys to import from the file")
    return parser


def many_from_path(bibpath):
    """Extract list of papers found in bibliographic files in path.

    The behavior is to:
        - ignore wrong entries,
        - overwrite duplicated entries.
    :returns: dictionary of (key, paper | exception)
        if loading of entry failed, the excpetion is returned in the
        dictionary in place of the paper
    """
    coder = endecoder.EnDecoder()

    bibpath = os.path.expanduser(bibpath)
    if os.path.isdir(bibpath):
        all_files = [os.path.join(bibpath, f) for f in os.listdir(bibpath)
                     if os.path.splitext(f)[-1][1:] in list(coder.decode_fmt.keys())]
    else:
        all_files = [bibpath]

    biblist = []
    for filepath in all_files:
        with open(filepath, 'r') as f:
            biblist.append(coder.decode_bibdata(f.read()))

    papers = {}
    for b in biblist:
        for k in b.entries:
            try:
                bibdata = BibliographyData()
                bibdata.entries[k] = b.entries[k]

                papers[k] = Paper(bibdata, citekey=k)
                papers[k].added = datetime.datetime.now()
            except ValueError, e:
                papers[k] = e
    return papers


def command(args):
    """
        :param bibpath: path (no url yet) to a bibliography file
    """

    ui = get_ui()
    bibpath = args.bibpath
    copy = args.copy

    if copy is None:
        copy = config().import_copy
    rp = repo.Repository(config())
    # Extract papers from bib
    papers = many_from_path(bibpath)
    keys = args.keys or papers.keys()
    for k in keys:
        try:
            p = papers[k]
            if isinstance(p, Exception):
                ui.error('could not load entry for citekey {}.'.format(k))
            else:
                docfile = bibstruct.extract_docfile(p.bibdata)
                if docfile is None:
                    ui.warning("no file for {}.".format(p.citekey))
                else:
                    copy_doc = args.copy
                    if copy_doc is None:
                        copy_doc = config().import_copy
                    if copy_doc:
                        docfile = rp.databroker.copy_doc(p.citekey, docfile)

                    p.docpath = docfile
                rp.push_paper(p)
                ui.print_('{} imported'.format(color.dye(p.citekey, color.cyan)))
        except KeyError:
            ui.error('no entry found for citekey {}.'.format(k))
        except IOError, e:
            ui.error(e.message)
