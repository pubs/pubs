import os
import shutil
import subprocess

from ... import repo
from ... import configs
from ... import files
from ...plugin import PapersPlugin
from ...commands.helpers import add_references_argument, parse_reference

from ...events import RemoveEvent


TEXNOTE_SECTION = 'texnote'
TEXNOTE_SAMPLE_FILE = os.path.join(os.path.dirname(__file__), 'note_sample.tex')
TEXNOTE_DIR = 'texnote'


class TexnotePlugin(PapersPlugin):

    def parser(self, subparsers, config):
        parser = subparsers.add_parser(self.name, help="edit advance note in latex")
        sub = parser.add_subparsers(title="valid texnote commands", dest="texcmd")
        p = sub.add_parser("remove", help="remove a reference")
        add_references_argument(p, single=True)
        p = sub.add_parser("edit", help="edit the reference texnote")
        add_references_argument(p, single=True)
        #add_references_argument(parser, single=True)
        parser.add_argument('-v', '--view', action='store_true', help='open the paper in a pdf viewer', default=None)
        return parser

    def command(self, config, ui, texcmd, reference, view):
        if view is not None:
            subprocess.Popen(['papers', 'open', reference])
        if texcmd == 'edit':
            open_texnote(config, ui, reference)

    def toto(self):
        print "toto"

    #@RemoveEvent.listen()
    def testEvent(self, rmevent):
        print "testEvent"


@RemoveEvent.listen()
def remove(rmevent):
    texplug = TexnotePlugin.get_instance()
    texplug.toto()
    rp = repo.Repository.from_directory(rmevent.config)
    paper = rp.get_paper(parse_reference(rmevent.ui, rp, rmevent.citekey))
    if 'texnote' in paper.metadata:
        try:
            os.remove(paper.metadata['texnote'])
        except OSError:
            pass  # For some reason, the texnote file didn't exist
        paper.metadata.pop('texnote')
        metapath = rp.path_to_paper_file(paper.citekey, 'meta')
        files.save_meta(paper.metadata, metapath)


def open_texnote(config, ui, ref):
    rp = repo.Repository.from_directory(config)
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
    if config.has_option(TEXNOTE_SECTION, 'edit-cmd'):
        #os.system(config.get(TEXNOTE_SECTION, 'edit-cmd') + ' ' + texnote_path + " &")
        subprocess.Popen([config.get(TEXNOTE_SECTION, 'edit-cmd'), texnote_path])
    else:
        #os.system(config.get(configs.MAIN_SECTION, 'edit-cmd') + ' ' + texnote_path + " &")
        subprocess.Popen([config.get(configs.MAIN_SECTION, 'edit-cmd'), texnote_path])


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
