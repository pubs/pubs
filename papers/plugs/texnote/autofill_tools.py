AUTOFILL_TPL = '\\autofill{FIELD}{INFO}'


def get_autofill_pattern(field):
    return AUTOFILL_TPL.replace('FIELD', field)


def autofill(text, paper):
    for field, info in get_autofill_info(paper):
        text = replace_pattern(text,
                               get_autofill_pattern(field),
                               info)
    return text

def get_autofill_info(paper):
    fields = paper.bibentry.fields

    info = []
    if 'year' in fields:
        info.append(('YEAR', fields['year']))
    if 'title' in fields:
        info.append(('TITLE', fields['title']))
    if 'abstract' in fields:
        info.append(('ABSTRACT', fields['abstract']))
    info.append(('AUTHOR', get_author_as_str(paper)))
    return info


def find_first_level_delimiter(text, opening='{', closing='}'):
    if opening in text:
        match = text.split(opening,1)[1]
        cnt = 1
        for index in xrange(len(match)):
            if match[index] in (opening + closing):
                cnt = (cnt + 1) if match[index] == opening else (cnt - 1)
            if not cnt:
                return match[:index]


def fill_pattern(pattern, info):
    return pattern.replace('INFO', info)


def find_pattern(text, pattern):
    look_at = pattern.replace('INFO}', '')
    found = []
    start = -1
    while True:
        start = text.find(look_at, start + 1)
        if start < 0:
            break
        delim_start = start + len(look_at) - 1
        repl = find_first_level_delimiter(text[delim_start:])
        found.append(pattern.replace('INFO', repl))
    return found


def replace_pattern(text, pattern, info):
    repl = fill_pattern(pattern, info)
    for found in find_pattern(text, pattern):
        print found
        text = text.replace(found, repl)
    return text


##### ugly replace by proper #####
def get_author_as_str(paper):
    persons = paper.bibentry.persons
    authors = []
    if 'author' in persons:
        for author in persons['author']:
            authors.append(format_author(author))
    return concatenate_authors(authors)


def format_author(author):
    first = author.first()
    middle = author.middle()
    last = author.last()
    formatted = ''
    if first:
        formatted += first[0]
    if middle:
        formatted += ' ' + middle[0] + '.'
    if last:
        formatted += ' ' + last[0]
    return formatted


def concatenate_authors(authors):
    concatenated = ''
    for a in range(len(authors)):
        if len(authors) > 1 and a > 0:
            if a == len(authors) - 1:
                concatenated += ' and '
            else:
                concatenated += ', '
        concatenated += authors[a]
    return concatenated
#####
