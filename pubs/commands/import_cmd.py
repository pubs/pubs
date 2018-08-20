from __future__ import unicode_literals

import os
import datetime

from .. import repo
from .. import endecoder
from .. import bibstruct
from .. import color
from .. import content
from ..paper import Paper
from ..uis import get_ui
from ..content import system_path, read_text_file
from ..command_utils import add_doc_copy_arguments


_ABORT_USE_IGNORE_MSG = "Aborting import. Use --ignore-malformed to ignore."
_IGNORING_MSG = " Ignoring it."


def parser(subparsers, conf):
    parser = subparsers.add_parser(
        'import',
        help='import paper(s) to the repository')
    parser.add_argument(
        'bibpath',
        help='path to bibtex, bibtexml or bibyaml file (or directory)')
    parser.add_argument(
        'keys', nargs='*',
        help="one or several keys to import from the file")
    parser.add_argument(
        '-O', '--overwrite', action='store_true', default=False,
        help="Overwrite keys already in the database")
    parser.add_argument(
        '-i', '--ignore-malformed', action='store_true', default=False,
        help="Ignore malformed and unreadable files and entries")
    add_doc_copy_arguments(parser, copy=False)
    return parser


def many_from_path(ui, bibpath, ignore=False):
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
        try:
            biblist.append(coder.decode_bibdata(read_text_file(filepath)))
        except coder.BibDecodingError:
            error = "Could not parse bibtex at {}.".format(filepath)
            if ignore:
                ui.warning(error + _IGNORING_MSG)
            else:
                ui.error(error + _ABORT_USE_IGNORE_MSG)
                ui.exit()

    papers = {}
    for b in biblist:
        for k, b in b.items():
            if k in papers:
                ui.warning('Duplicated citekey {}. Keeping the last one.'.format(k))
            try:
                papers[k] = Paper(k, b)
                papers[k].added = datetime.datetime.now()
            except ValueError as e:
                error = 'Could not load entry for citekey {} ({}).'.format(k, e)
                if ignore:
                    ui.warning(error + _IGNORING_MSG)
                else:
                    ui.error(error + _ABORT_USE_IGNORE_MSG)
                    ui.exit()
    return papers


def command(conf, args):
    """
        :param bibpath: path (no url yet) to a bibliography file
    """

    ui = get_ui()
    bibpath = args.bibpath
    doc_import = args.doc_copy or 'copy'

    rp = repo.Repository(conf)
    # Extract papers from bib
    papers = many_from_path(ui, bibpath, ignore=args.ignore_malformed)
    keys = args.keys or papers.keys()
    for k in keys:
        p = papers[k]
        rp.push_paper(p, overwrite=args.overwrite)
        ui.info('{} imported.'.format(color.dye_out(p.citekey, 'citekey')))
        docfile = bibstruct.extract_docfile(p.bibdata)
        if docfile is None:
            ui.warning("No file for {}.".format(p.citekey))
        else:
            rp.push_doc(p.citekey, docfile,
                        copy=(doc_import in ('copy', 'move')))
            if doc_import == 'move' and content.content_type(docfile) != 'url':
                content.remove_file(docfile)

    rp.close()
