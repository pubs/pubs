import os
import shutil
import subprocess
import collections

from ... import repo
from ... import files
from ...configs import config
from ...plugins import PapersPlugin
from ...commands.helpers import add_references_argument, parse_reference

from ...events import RemoveEvent, RenameEvent, AddEvent

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

    def _ensure_init(self):
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
        p.add_argument('-w', '--with', dest='with_command', default=None,
                       help='command to use to open the file')
        add_references_argument(p, single=True)
        # edit_style
        p = sub.add_parser('edit_style', help='edit the latex style used by texnote')
        p.add_argument('-w', '--with', dest='with_command', default=None,
                       help='command to use to open the file')
        #edit_template
        p = sub.add_parser('edit_template', help='edit the latex template used by texnote')
        p.add_argument('-w', '--with', dest='with_command', default=None,
                       help='command to use to open the file')
        return parser

    def command(self, args):
        self._ensure_init()

        texcmd = args.texcmd
        del args.texcmd
        self.texcmds[texcmd](**vars(args))

    def _texfile(self, citekey):
        return os.path.join(TEXNOTE_DIR, citekey + '.tex')

    def _ensure_texfile(self, citekey):
        if not files.check_file(self._texfile(citekey)):
            shutil.copy(TEXNOTE_TEMPLATE, self._texfile(citekey))

    def _autofill_texfile(self, citekey):
        self._ensure_texfile(citekey)

        with open(self._texfile(citekey)) as f:
            text = f.read()

        # modify with bib info
        rp = repo.Repository(config())
        paper = rp.get_paper(citekey)
        fields = paper.bibentry.fields
        persons = paper.bibentry.persons

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

        with open(self._texfile(citekey), "w") as f:
            f.write(text)

    def get_texfile(self, citekey):
        """ This function returns the name of the texfile and
        ensure it exist and it is filled with info from the bibfile"""
        self._autofill_texfile(citekey)
        return self._texfile(citekey)

    def get_edit_cmd(self):
        default = config().edit_cmd
        return config(TEXNOTE_SECTION).get('edit_cmd', default)

    def edit(self, ui, reference, view=None, with_command=None):
        if view is not None:
            subprocess.Popen(['papers', 'open', reference])
        if with_command is None:
            with_command = self.get_edit_cmd()

        rp = repo.Repository(config())
        citekey = parse_reference(ui, rp, reference)
        files.edit_file(with_command, self.get_texfile(citekey), temporary=False)

    def edit_style(self, ui, with_command=None):
        if with_command is None:
            with_command = self.get_edit_cmd()
        files.edit_file(with_command, TEXNOTE_STYLE, temporary=False)

    def edit_template(self, ui, with_command=None):
        if with_command is None:
            with_command = self.get_edit_cmd()
        files.edit_file(with_command, TEXNOTE_TEMPLATE, temporary=False)

    def create(self, citekey):
        self._autofill_texfile(citekey)

    def remove(self, citekey):
        try:
            os.remove(self._texfile(citekey))
        except OSError:
            pass  # For some reason, the texnote file didn't exist

    def rename(self, old_citekey, new_citekey, overwrite=False):
        if files.check_file(self._texfile(old_citekey)):
            if not files.check_file(self._texfile(new_citekey)) or overwrite:
                shutil.move(self._texfile(old_citekey), self._texfile(new_citekey))
            else:
                raise ValueError('citekey {} already exist'.format(new_citekey))
        else:
            raise ValueError('citekey {} does not exist'.format(old_citekey))


@AddEvent.listen()
def create(addevent):
    texplug = TexnotePlugin.get_instance()
    texplug.create(addevent.citekey)


@RemoveEvent.listen()
def remove(rmevent):
    texplug = TexnotePlugin.get_instance()
    texplug.remove(rmevent.citekey)


@RenameEvent.listen()
def rename(renamevent):
    texplug = TexnotePlugin.get_instance()
    texplug.rename(renamevent.old_citekey,
                   renamevent.paper.citekey,
                   overwrite=True)


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
