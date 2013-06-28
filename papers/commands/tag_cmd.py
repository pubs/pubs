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
5. > papers tag citekey math,romance,:war
    Add 'math' and 'romance' tags to the given citekey, and remove the 'war' tag
6. > papers tag math
    If 'math' is not a citekey, then display all papers with the tag 'math'
"""

from ..repo import Repository, InvalidReference
from . import helpers

def parser(subparsers, config):
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
    tags = []
    if s[0] not in ['+', '-']:
        s = '+' + s
    last = 0
    for m in re.finditer(r'[+-]', s):
        if m.start() == last:
            if last != 0:
                raise ValueError, 'could not match tag expression'
        else:
            tags.append(s[last:(m.start())])
        last = m.start()
    if last == len(s):
        raise ValueError, 'could not match tag expression'
    else:
        tags.append(s[last:])
    return tags


def command(config, ui, referenceOrTag, tags):
    """Add, remove and show tags"""
    rp = Repository.from_directory(config)

    if referenceOrTag is None:
        for tag in rp.get_tags():
            ui.print_(tag)
    else:
        try:
            citekey = rp.citekey_from_ref(referenceOrTag)
            p = rp.get_paper(citekey)
            if tags is None:
                ui.print_(' '.join(p.tags))
            else:
                tags = tags.split(',')
                for tag in tags:
                    if tag[0] == ':':
                        p.remove_tag(tag[1:])
                    else:
                        p.add_tag(tag)
                rp.save_paper(p)
        except InvalidReference:
            tag = referenceOrTag
            papers_list = [(p, n) for n, p in enumerate(rp.all_papers())
                           if tag in p.tags]
            ui.print_('\n'.join(helpers.paper_oneliner(p, n)
                                for p, n in papers_list))