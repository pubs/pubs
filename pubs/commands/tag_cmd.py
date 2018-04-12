"""
This command is all about tags.
The different use cases are :
1. > pubs tag
    Returns the list of all tags
2. > pubs tag citekey
    Return the list of tags of the given citekey
3. > pubs tag citekey math
    Add 'math' to the list of tags of the given citekey
4. > pubs tag citekey :math
    Remove 'math' for the list of tags of the given citekey
5. > pubs tag citekey math+romance-war
    Add 'math' and 'romance' tags to the given citekey, and remove the 'war' tag
6. > pubs tag math
    If 'math' is not a citekey, then display all papers with the tag 'math'
7. > pubs tag -war+math+romance
    display all papers with the tag 'math', 'romance' but not 'war'
"""
from __future__ import unicode_literals

import re

from ..repo import Repository
from ..uis import get_ui
from .. import pretty
from .. import color
from ..utils import resolve_citekey
from ..completion import CiteKeyOrTagCompletion, TagModifierCompletion


def parser(subparsers, conf):
    parser = subparsers.add_parser('tag', help="add, remove and show tags")
    parser.add_argument('citekeyOrTag', nargs='?', default=None,
                        help='citekey or tag.').completer = CiteKeyOrTagCompletion(conf)
    parser.add_argument('tags', nargs='?', default=None,
                        help='If the previous argument was a citekey, then '
                             'a list of tags separated by + and -.'
                        ).completer = TagModifierCompletion(conf)
    # TODO find a way to display clear help for multiple command semantics,
    #      indistinguisable for argparse. (fabien, 201306)
    return parser


def _parse_tag_seq(s):
    """Transform 'math-ai' in ['+math', '-ai']"""
    tags = []
    if s[0] == ':':
        s = '-' + s[1:]
    if s[0] not in ['+', '-']:
        s = '+' + s
    last = 0
    for m in re.finditer(r'[+-]', s):
        if m.start() == last:
            if last != 0:
                raise ValueError('could not match tag expression')
        else:
            tags.append(s[last:(m.start())])
        last = m.start()
    if last == len(s):
        raise ValueError('could not match tag expression')
    else:
        tags.append(s[last:])
    return tags


def _tag_groups(tags):
    plus_tags, minus_tags = [], []
    for tag in tags:
        if tag[0] == '+':
            plus_tags.append(tag[1:])
        else:
            assert tag[0] == '-'
            minus_tags.append(tag[1:])
    return set(plus_tags), set(minus_tags)


def command(conf, args):
    """Add, remove and show tags"""

    ui = get_ui()
    citekeyOrTag = args.citekeyOrTag
    tags = args.tags

    rp = Repository(conf)

    if citekeyOrTag is None:
        ui.message(color.dye_out(' '.join(sorted(rp.get_tags())), 'tag'))
    else:
        not_citekey = False
        try:
            citekeyOrTag = resolve_citekey(repo=rp, citekey=citekeyOrTag, ui=ui, exit_on_fail=True)
        except SystemExit:
            not_citekey = True
        if not not_citekey:
            p = rp.pull_paper(citekeyOrTag)
            if tags is None:
                ui.message(color.dye_out(' '.join(sorted(p.tags)), 'tag'))
            else:
                add_tags, remove_tags = _tag_groups(_parse_tag_seq(tags))
                for tag in add_tags:
                    p.add_tag(tag)
                for tag in remove_tags:
                    p.remove_tag(tag)
                rp.push_paper(p, overwrite=True)
        elif tags is not None:
            ui.error(ui.error('No entry found for citekey {}.'.format(citekeyOrTag)))
            ui.exit()
        else:
            ui.info('Assuming {} to be a tag.'.format(color.dye_out(citekeyOrTag)))
            # case where we want to find papers with specific tags
            included, excluded = _tag_groups(_parse_tag_seq(citekeyOrTag))
            papers_list = []
            for p in rp.all_papers():
                if (p.tags.issuperset(included) and
                    len(p.tags.intersection(excluded)) == 0):
                    papers_list.append(p)

            ui.message('\n'.join(pretty.paper_oneliner(p)
                                 for p in papers_list))

        rp.close()
