from __future__ import unicode_literals

from ..paper import Paper
from .. import repo

from ..uis import get_ui
from ..endecoder import EnDecoder
from ..utils import resolve_citekey
from ..completion import CiteKeyCompletion


def parser(subparsers, conf):
    parser = subparsers.add_parser(
        'edit',
        help='open the paper bibliographic file in an editor')
    parser.add_argument(
        '-m', '--meta', action='store_true', default=False,
        help='edit metadata')
    parser.add_argument(
        'citekey',
        help='citekey of the paper').completer = CiteKeyCompletion(conf)
    return parser


def command(conf, args):

    ui = get_ui()
    meta = args.meta

    rp = repo.Repository(conf)
    citekey = resolve_citekey(rp, args.citekey, ui=ui, exit_on_fail=True)
    paper = rp.pull_paper(citekey)

    coder = EnDecoder()
    if meta:
        encode = coder.encode_metadata
        decode = coder.decode_metadata
        suffix = '.yaml'
        raw_content = encode(paper.metadata)
    else:
        encode = coder.encode_bibdata
        decode = coder.decode_bibdata
        suffix = '.bib'
        raw_content = encode(paper.bibentry)

    while True:
        # Get new content from user
        raw_content = ui.editor_input(initial=raw_content, suffix=suffix)
        # Parse new content
        try:
            content = decode(raw_content)

            if meta:
                new_paper = Paper(paper.citekey, paper.bibdata,
                                  metadata=content)
                rp.push_paper(new_paper, overwrite=True, event=False)
                ui.info(('The metadata of paper `{}`  was successfully '
                         'edited.'.format(citekey)))
            else:
                new_paper = Paper.from_bibentry(content,
                                                metadata=paper.metadata)
                if rp.rename_paper(new_paper, old_citekey=paper.citekey):
                    ui.info(('Paper `{}` was successfully edited and renamed '
                             'as `{}`.'.format(citekey, new_paper.citekey)))
                else:
                    ui.info(('Paper `{}` was successfully edited.'.format(
                        citekey)))
            break

        except coder.BibDecodingError:
            if not ui.input_yn(question="Error parsing bibdata. Edit again?"):
                ui.error("Aborting, paper not updated.")
                ui.exit()

        except repo.CiteKeyCollision:
            options = ['overwrite', 'edit again', 'abort']
            choice = options[ui.input_choice(
                options, ['o', 'e', 'a'],
                question='A paper already exists with this citekey.'
            )]

            if choice == 'abort':
                break
            elif choice == 'overwrite':
                paper = rp.push_paper(paper, overwrite=True)
                ui.info(('Paper `{}` was overwritten.'.format(citekey)))
                break
            # else edit again
        # Also handle malformed bibtex and metadata

    rp.close()
