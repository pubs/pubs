# Pubs

Pubs brings your bibliography to the command line.

Pubs organizes your bibliographic documents together with the bibliographic data associated to them and provides command line access to basic and advanced manipulation of your library.

Pubs is built with the following principles in mind:

 - all papers are referenced using unique citation keys,
 - bibliographic data (i.e. pure bibtex information) is kept separated from metadata (including links to pdf or tags),
 - everything is stored in plain text so it can be manually edited or version controlled.

**Notice:** pubs is still in early development; you should regularly make backups of your pubs repository.


## Installation

Until pubs is uploaded to Pypi, the standard way to install it is to clone the repository and call `setup.py`.

    git clone https://github.com/pubs/pubs.git
    cd pubs
    sudo python setup.py install # remove sudo and add --user for local installation instead

Alternatively Arch Linux users can also use the [pubs-git](https://aur.archlinux.org/packages/pubs-git/) AUR package.


## Getting started

Create your library (by default, goes to `~/.pubs/`).

    pubs init

Import existing data from bibtex (pubs will try to automatically copy documents defined as 'file' in bibtex):

    pubs import path/to/collection.bib

or for a .bib file containing a single reference:

    pubs add reference.bib -d article.pdf

pubs can also automatically retrieve the bibtex from a doi:

    pubs add -D 10.1007/s00422-012-0514-6 -d article.pdf

or an ISBN (dashes are ignored):

    pubs add -I 978-0822324669 -d article.pdf


## References always up-to-date

If you use latex, you can automatize references, by creating a bash script with:

    #!/bin/bash
    pubs export > references.bib
    latex manuscript.tex
    bibtex manuscript
    latex manuscript.tex

This ensures that your reference file is always up-to-date; you can cite a paper in your manuscript a soon as you add it in pubs. This means that if you have, for instance, a doi on a webpage, you only need to do:

    pubs add -D 10.1007/s00422-012-0514-6

and then add `\cite{Loeb_2012}` in your manuscript. After running the bash script, the citation will correctly appear in your compiled pdf.


## Document management

You can attach a document to a reference:

    pubs add Loeb2012_downloaded.pdf Loeb_2012

And open your documents automatically from the command line:

    pubs doc open Loeb_2012


## Customization

Pubs is designed to interact well with your command line tool chain.
You can add custom commands to pubs by defining aliases in your config file (make sure that the alias plugin is activated in your configuration by using `pubs conf`).

    [[alias]]
    evince = open --with evince
    count = !pubs list -k | wc -l

The first command defines a new subcommand: `pubs open -w evince` will be executed when `pubs evince` is typed.
The second starts with a bang: `!`, and is treated as a shell command.


## Autocompletion

For autocompletion to work, you need the [argcomplete](https://argcomplete.readthedocs.io) python package.

For bash completion, just activate it globally with the command `activate-global-python-argcomplete`, or `activate-global-python-argcomplete --user`, that will copy `python-argcomplete.sh` to `/etc/bash_completion.d/` or `~/.bash_completion.d/`. You need to make sure that the file is evaluated on bash start. For more information or other shells please report to [argcomplete's documentation](https://argcomplete.readthedocs.io).


## Need more help ?

You can access the self-documented configuration by using `pubs conf`, and all the commands's help is available with the `--help` option. Did not find an answer to your question? Drop us an issue. We may not answer right away (science comes first!) but we'll eventually look into it.


## Requirements

- python >= 2.7 or >= 3.3
- [argcomplete](https://argcomplete.readthedocs.io) (optional, for autocompletion)

## Authors

- [Fabien Benureau](http://fabien.benureau.com)
- [Olivier Mangin](http://olivier.mangin.com)
- Jonathan Grizou
- Arnold Sykosch
