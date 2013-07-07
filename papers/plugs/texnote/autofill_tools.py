AUTOFILL_TPL = '\\autofill{FIELD}{INFO}'


def get_autofill_pattern(field):
    return AUTOFILL_TPL.replace('FIELD', field)


def autofill(text, paper):
    for field, info in get_autofill_info(paper):
        print find_pattern(text, get_autofill_pattern(field))
        print fill_pattern(get_autofill_pattern(field), info)
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


def fill_pattern(pattern, info):
    return pattern.replace('INFO', info)


def find_pattern(text, pattern):
    pattern = pattern.replace('INFO}', '')
    start = text.find(pattern)
    after = start + len(pattern)
    info_length = text[after:].find('}')
    end = start + len(pattern) + info_length + 1
    return text[start:end]


def replace_pattern(text, pattern, info):
        return text.replace(find_pattern(text, pattern),
                            fill_pattern(pattern, info))


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
