import os
import datetime

from .. import repo
from .. import endecoder
from .. import bibstruct
from .. import color
from ..paper import Paper

from ..uis import get_ui
from ..content import system_path, read_text_file


def parser(subparsers, conf):
    parser = subparsers.add_parser('import',
            help='import paper(s) to the repository')
    parser.add_argument('bibpath',
            help='path to bibtex, bibtexml or bibyaml file (or directory)')
    parser.add_argument('-L', '--link', action='store_false', dest='copy', default=True,
            help="don't copy document files, just create a link.")
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

    bibpath = system_path(bibpath)
    if os.path.isdir(bibpath):
        print([os.path.splitext(f)[-1][1:] for f in os.listdir(bibpath)])
        all_files = [os.path.join(bibpath, f) for f in os.listdir(bibpath)
                     if os.path.splitext(f)[-1][1:] == 'bib']
    else:
        all_files = [bibpath]

    biblist = []
    for filepath in all_files:
        biblist.append(coder.decode_bibdata(read_text_file(filepath)))

    papers = {}
    for b in biblist:
        for k, b in b.items():
            try:
                papers[k] = Paper(k, b)
                papers[k].added = datetime.datetime.now()
            except ValueError as e:
                papers[k] = e
    return papers


def command(conf, args):
    """
        :param bibpath: path (no url yet) to a bibliography file
    """

    ui = get_ui()
    bibpath = args.bibpath
    copy = args.copy
    if copy is None:
        copy = conf['main']['doc_add'] in ('copy', 'move')

    rp = repo.Repository(conf)
    # Extract papers from bib
    papers = many_from_path(bibpath)
    keys = args.keys or papers.keys()
    for k in keys:
        p = papers[k]
        if isinstance(p, Exception):
            ui.error(u'Could not load entry for citekey {}.'.format(k))
        else:
            rp.push_paper(p)
            ui.info(u'{} imported.'.format(color.dye_out(p.citekey, 'citekey')))
            docfile = bibstruct.extract_docfile(p.bibdata)
            if docfile is None:
                ui.warning("No file for {}.".format(p.citekey))
            else:
                rp.push_doc(p.citekey, docfile, copy=copy)
                #FIXME should move the file if configured to do so.

    rp.close()
