from __future__ import unicode_literals

import os
import datetime

from .. import repo
from .. import endecoder
from .. import bibstruct
from .. import color
from .. import content
from .. import pretty
from .. import config
from ..paper import Paper
from ..uis import get_ui
from ..content import system_path, read_text_file
from ..command_utils import add_doc_copy_arguments


_ABORT_USE_IGNORE_MSG = " Aborting import. Use --ignore-malformed to ignore."
_IGNORING_MSG = " Ignoring it."


def parser(subparsers, conf):
    parser = subparsers.add_parser(
        'import',
        help='import paper(s) to the repository.')
    parser.add_argument(
        'bibpath',
        help=("path to bibtex, bibtexml or bibyaml file, or a directory "
              "containing such files; will not recurse into subdirectories."))
    parser.add_argument(
        'keys', nargs='*',
        help=("one or several keys to import from the file; if not provided,"
              " all entries will be imported."))
    parser.add_argument(
        '-O', '--overwrite', action='store_true', default=False,
        help="overwrite keys already in the database.")
    parser.add_argument(
        '-i', '--ignore-malformed', action='store_true', default=False,
        help="ignore malformed and unreadable files and entries.")
    parser.add_argument(
        '-l', '--list-only', action='store_true', default=False,
        help="only list found entries, do not import.")
    parser.add_argument(
        '--source', choices=['pubs', 'bibtex'],
        help="set source type: can be pubs repository or bibtex file(s).")
    add_doc_copy_arguments(parser, copy=False)
    return parser


def is_probably_repo(bibpath):
    """Guess if path is pubs repository.

    Uses a simple heuristic: check if contains expected subdirectories.
    """
    if os.path.isdir(bibpath):
        subdirs = next(os.walk(bibpath))[1]
        return set(subdirs).issuperset(['bib', 'meta'])
    else:
        return False


def many_from_repo(bibpath):
    default_config = config.load_default_conf()
    # TODO: improve this (and make robust to missing doc directory)
    default_config['main']['pubsdir'] = bibpath
    default_config['main']['docsdir'] = os.path.join(default_config['main']['pubsdir'], 'doc')
    rp = repo.Repository(default_config)
    # TODO: probably disable caching?
    return rp, rp.all_papers()


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
    # Extract papers from source
    # TODO: improve logic
    # TODO: import from pubs config
    if (args.source == 'pubs' or (args.source is None and is_probably_repo(bibpath))):
        source_repo, papers = many_from_repo(bibpath)
        papers = {p.citekey: p for p in papers}
    else:
        source_repo = None
        papers = many_from_path(ui, bibpath, ignore=args.ignore_malformed)

    keys = args.keys or papers.keys()
    for k in keys:
        p = papers[k]

        # Attempts to find a document
        # TODO: use better logic
        docfile = None
        if source_repo is not None and p.docpath:
            docfile = source_repo.pull_docpath(k)
        if docfile is None:
            docfile = bibstruct.extract_docfile(p.bibdata)

        if args.list_only:
            paper_str = pretty.paper_oneliner(p)
            if docfile is not None:
                paper_str += "\n  ↳ found doc: {}".format(docfile)
            ui.message(paper_str)
        else:
            try:
                # TODO: update "add date & time" to match original
                rp.push_paper(p, overwrite=args.overwrite)
            except repo.CiteKeyCollision:
                ui.warning("{} already in repository, use '-O' to overwrite".format(
                        color.dye_out(p.citekey, 'citekey')
                    )
                )
                continue
            ui.info('{} imported.'.format(color.dye_out(p.citekey, 'citekey')))
            if docfile is None:
                ui.warning("No file for {}.".format(p.citekey))
            else:
                rp.push_doc(p.citekey, docfile,
                            copy=(doc_import in ('copy', 'move')))
                if doc_import == 'move' and content.content_type(docfile) != 'url':
                    content.remove_file(docfile)

    rp.close()
