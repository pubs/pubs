import os
import shutil
import subprocess
import collections

from ... import repo
from ... import files
from ...configs import config
from ...plugins import PapersPlugin
from ...commands.helpers import add_references_argument, parse_reference

from ...events import RemoveEvent

TEXNOTE_SECTION = 'texnote'
TEXNOTE_DIR = os.path.join(config().papers_dir, 'texnote')
TEXNOTE_TEMPLATE = os.path.join(TEXNOTE_DIR, 'template.tex')
TEXNOTE_STYLE = os.path.join(TEXNOTE_DIR, 'style.sty')

TEXNOTE_DEFAULT_TEMPLATE = os.path.join(os.path.dirname(__file__), 'template.tex')
TEXNOTE_DEFAULT_STYLE = os.path.join(os.path.dirname(__file__), 'style.sty')


class TexnotePlugin(PapersPlugin):

    def __init__(self):
        self.name = TEXNOTE_SECTION

        self.texcmds = collections.OrderedDict([
                        ('remove', self.remove),
                        ('edit', self.edit),
                        ('edit_style', self.edit_style),
                        ('edit_template', self.edit_template),
                        ])

    def ensure_init(self):
        if not files.check_directory(TEXNOTE_DIR):
            os.mkdir(TEXNOTE_DIR)
        if not files.check_file(TEXNOTE_TEMPLATE):
            shutil.copy(TEXNOTE_DEFAULT_TEMPLATE, TEXNOTE_TEMPLATE)
        if not files.check_file(TEXNOTE_STYLE):
            shutil.copy(TEXNOTE_DEFAULT_STYLE, TEXNOTE_STYLE)

    def parser(self, subparsers):
        parser = subparsers.add_parser(self.name, help='edit advance note in latex')
        sub = parser.add_subparsers(title='valid texnote commands', dest='texcmd')
        # remove
        p = sub.add_parser('remove', help='remove a reference')
        add_references_argument(p, single=True)
        # edit
        p = sub.add_parser('edit', help='edit the reference texnote')
        p.add_argument('-v', '--view', action='store_true',
                help='open the paper in a pdf viewer', default=None)
        add_references_argument(p, single=True)
        # edit_style
        p = sub.add_parser('edit_style', help='edit the latex style used by texnote')
        #edit_template
        p = sub.add_parser('edit_template', help='edit the latex template used by texnote')
        return parser

    def command(self, args):
        self.ensure_init()

        texcmd = args.texcmd
        del args.texcmd
        self.texcmds[texcmd](**vars(args))

    def remove(self, ui, reference):
        rp = repo.Repository(config())
        key = parse_reference(ui, rp, reference)
        print('Should remove {}'.format(key))

    def edit(self, ui, reference, view=None):
        print('Should edit {}'.format(reference))
        if view is not None:
            subprocess.Popen(['papers', 'open', reference])

        #open_texnote(ui, reference)

    def edit_style(self):
        pass

    def edit_template(self):
        pass

    def toto(self):
        print "toto"

    #@RemoveEvent.listen()
    def testEvent(self, rmevent):
        print "testEvent"


@RemoveEvent.listen()
def remove(rmevent):
    texplug = TexnotePlugin.get_instance()
    texplug.remove(rmevent.ui, rmevent.citekey)
    # HACK : transfer repo via RemoveEvent, do not recreate one
    #rp = repo.Repository(config())
    #paper = rp.get_paper(parse_reference(rmevent.ui, rp, rmevent.citekey))
    #if 'texnote' in paper.metadata:
    #    try:
    #        os.remove(paper.metadata['texnote'])
    #    except OSError:
    #        pass  # For some reason, the texnote file didn't exist
    #    paper.metadata.pop('texnote')
    #    metapath = rp.path_to_paper_file(paper.citekey, 'meta')
    #    files.save_meta(paper.metadata, metapath)


def open_texnote(ui, ref):
    # HACK : transfer repo via arguments, do not recreate one
    rp = repo.Repository(config())
    paper = rp.get_paper(parse_reference(ui, rp, ref))

    #ugly to recode like for the doc field
    if not 'texnote' in paper.metadata:
        texnote_dir = os.path.join(rp.papersdir, TEXNOTE_DIR)
        # if folder does not exist create it, this should be relative
        if not os.path.exists(texnote_dir):
            os.mkdir(texnote_dir)
        texnote_path = os.path.join(texnote_dir, paper.citekey + '.tex')
        paper.metadata['texnote'] = files.clean_path(texnote_path)
        # save path in metadata
        metapath = rp.path_to_paper_file(paper.citekey, 'meta')
        files.save_meta(paper.metadata, metapath)

    texnote_path = paper.metadata['texnote']
    # test if doc exist else copy the sample one
    if not files.check_file(texnote_path):
        shutil.copyfile(TEXNOTE_SAMPLE_FILE, texnote_path)
    #should autofill at every opening or not ? usefull if bib changes but the filling should be improved
    autofill_texnote(texnote_path, paper.bibentry)

    #open the file using the config editor
    edit_cmd = config(TEXNOTE_SECTION).get('edit_cmd', config().edit_cmd)
    subprocess.Popen([edit_cmd, texnote_path])


##### ugly replace by proper #####
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
                concatenated += 'and '
            else:
                concatenated += ', '
        concatenated += authors[a]
    return concatenated
#####


def autofill_texnote(texnote_path, bibentry):
    # read file
    f = open(texnote_path, "r")
    text = f.read()
    f.close()
    # modify with bib info
    #print bibentry
    fields = bibentry.fields
    persons = bibentry.persons

    if 'title' in fields:
        title_str = fields['title']
        text = text.replace("TITLE", title_str)

    if 'year' in fields:
        year_str = fields['year']
        text = text.replace("YEAR", year_str)

    if 'abstract' in fields:
        abstract_str = fields['abstract']
        text = text.replace("ABSTRACT", abstract_str)

    if 'author' in persons:
        authors = []
        for author in persons['author']:
            authors.append(format_author(author))
        author_str = concatenate_authors(authors)
        text = text.replace("AUTHOR", author_str)

    # write file
    f = open(texnote_path, "w")
    f.write(text)
    f.close()
