"""
This command is all about tags.
The different use cases are :
1. > papers tag
    Returns the list of all tags
2. > papers tag citekey
    Return the list of tags of the given citekey
3. > papers tag citekey math
    Add 'math' to the list of tags of the given citekey
4. > papers tag citekey :math
    Remove 'math' for the list of tags of the given citekey
5. > papers tag citekey math+romance-war
    Add 'math' and 'romance' tags to the given citekey, and remove the 'war' tag
6. > papers tag math
    If 'math' is not a citekey, then display all papers with the tag 'math'
7. > papers tag -war+math+romance
    display all papers with the tag 'math', 'romance' but not 'war'
"""

from ..repo import Repository, InvalidReference
from . import helpers
from ..configs import config

def parser(subparsers):
    parser = subparsers.add_parser('tag', help="add, remove and show tags")
    parser.add_argument('referenceOrTag', nargs='?', default = None,
                        help='reference to the paper (citekey or number), or '
                             'tag.')
    parser.add_argument('tags', nargs='?', default = None,
                        help='If the previous argument was a reference, then '
                             'then a list of tags separated by commas.')
    # TODO find a way to display clear help for multiple command semantics,
    #      indistinguisable for argparse. (fabien, 201306)
    return parser


import re
def _parse_tags(s):
    """Transform 'math-ai' in ['+math', '-ai']"""
    tags = []
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

def command(ui, referenceOrTag, tags):
    """Add, remove and show tags"""
    rp = Repository(config())

    if referenceOrTag is None:
        for tag in rp.get_tags():
            ui.print_(tag)
    else:
        try:
            citekey = rp.ref2citekey(referenceOrTag)
            p = rp.get_paper(citekey)
            if tags is None:
                ui.print_(' '.join(p.tags))
            else:
                add_tags, remove_tags = _tag_groups(_parse_tags(tags))
                for tag in add_tags:
                    p.add_tag(tag)
                for tag in remove_tags:
                    p.remove_tag(tag)
                rp.save_paper(p)
        except InvalidReference:
            # case where we want to find paper with specific tags
            included, excluded = _tag_groups(_parse_tags(referenceOrTag))
            papers_list = []
            for n, p in enumerate(rp.all_papers()):
                if (p.tags.issuperset(included) and
                    len(p.tags.intersection(excluded)) == 0):
                    papers_list.append((p, n))

            ui.print_('\n'.join(helpers.paper_oneliner(p, n)
                                for p, n in papers_list))