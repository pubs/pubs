#import ConfigParser

#from ... import configs
#cfg = configs.read_config()

#TEXNOTE_SECTION = 'texnote'
#DEFAULT_EDIT_CMD = cfg.get(configs.MAIN_SECTION, 'edit-cmd')

#TODO file should not be created before the end of the process to ensure everything went ok
#TODO add subparser to have more feature
#TODO add clean command to wipe out any compilation file
#TODO add function to merge several texnote in one based on a research result

import os
import shutil
import subprocess

from ...color import colored
from ... import repo
from ...paper import NoDocumentFile
from ... import configs
from ... import files

TEXNOTE_SECTION = 'texnote'
TEXNOTE_SAMPLE_FILE = os.path.join(os.path.dirname(__file__), 'note_sample.tex')
TEXNOTE_DIR = 'texnote'

def parser(subparsers, config):
    parser = subparsers.add_parser('texnote', help="edit advance note in latex")
    parser.add_argument('ref', help='the paper associated citekey or number')
    parser.add_argument('-v', '--view', action='store_true', help='open the paper in a pdf viewer', default=None)
    return parser


def command(config, ui, ref, view):
    ui.print_('texnote test')
    if view is not None:
        subprocess.Popen(['papers', 'open', ref])

    # check if citekey exist
    open_texnote(config, ui, ref)



def open_texnote(config, ui, ref):
    rp = repo.Repository.from_directory(config)
    paper = rp.paper_from_ref(ref, fatal=True)

    if not paper.metadata.has_key('texnote'):
        texnote_dir = os.path.join(rp.papersdir, TEXNOTE_DIR)
        # if folder does not exist create it
        if not os.path.exists(texnote_dir):
            os.mkdir(texnote_dir)
        texnote_path = os.path.join(texnote_dir, paper.citekey + '.tex')
        paper.metadata['texnote'] =  files.clean_path(texnote_path)
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
            else :
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
    print bibentry
    fields = bibentry.fields
    persons = bibentry.persons

    if fields.has_key('title'):
        title_str = fields['title']
        text = text.replace("TITLE", title_str)

    if fields.has_key('year'):
        year_str = fields['year']
        text = text.replace("YEAR", year_str)

    if fields.has_key('abstract'):
        abstract_str = fields['abstract']
        text = text.replace("ABSTRACT", abstract_str)

    if persons.has_key('author'):
        authors = []
        for author in persons['author']:
            authors.append(format_author(author))
        author_str =  concatenate_authors(authors)
        text = text.replace("AUTHOR", author_str)

    # write file
    f = open(texnote_path, "w")
    f.write(text)
    f.close()
