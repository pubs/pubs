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

import re

from ..repo import Repository
from ..configs import config
from ..uis import get_ui
from .. import pretty
from .. import color


def parser(subparsers):
    parser = subparsers.add_parser('tag', help="add, remove and show tags")
    parser.add_argument('citekeyOrTag', nargs='?', default=None,
                        help='citekey or tag.')
    parser.add_argument('tags', nargs='*', default=None,
                        help='If the previous argument was a citekey, then '
                             'a list of tags separated by a +.')
    # TODO find a way to display clear help for multiple command semantics,
    #      indistinguisable for argparse. (fabien, 201306)
    return parser


def _parse_tags(list_tags):
    """Transform 'math-ai network -search' in ['+math', '-ai', '+network', '-search']"""
    tags = []
    for s in list_tags:
        tags += _parse_tag_seq(s)
    return tags


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


def command(args):
    """Add, remove and show tags"""

    ui = get_ui()
    citekeyOrTag = args.citekeyOrTag
    tags = args.tags

    rp = Repository(config())

    if citekeyOrTag is None:
        ui.message(color.dye_out(' '.join(sorted(rp.get_tags())), color.tag))
    else:
        if rp.databroker.exists(citekeyOrTag):
            p = rp.pull_paper(citekeyOrTag)
            if tags == []:
                ui.message(color.dye_out(' '.join(sorted(p.tags)), color.tag))
            else:
                add_tags, remove_tags = _tag_groups(_parse_tags(tags))
                for tag in add_tags:
                    p.add_tag(tag)
                for tag in remove_tags:
                    p.remove_tag(tag)
                rp.push_paper(p, overwrite=True)
        else:
            # case where we want to find papers with specific tags
            all_tags = [citekeyOrTag]
            all_tags += tags
            included, excluded = _tag_groups(_parse_tags(all_tags))
            papers_list = []
            for p in rp.all_papers():
                if (p.tags.issuperset(included) and
                    len(p.tags.intersection(excluded)) == 0):
                    papers_list.append(p)

            ui.message('\n'.join(pretty.paper_oneliner(p)
                                 for p in papers_list))
