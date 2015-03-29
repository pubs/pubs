# Pubs

Pubs brings your bibliography to the command line.

Pubs organizes your bibliographic documents together with the bibliographic data associated to them and provides command line access to basic and advanced manipulation of your library.

Pubs is built with the following principles in mind:

 - all papers are referenced using unique citation keys,
 - bibliographic data (i.e. pure bibtex information) is kept separated from metadata (including links to pdf or tags),
 - everything is stored in plain text so it can be manually edited or version controlled.


**Notice:** pubs is still in early development and cannot be considered as stable


Getting started
---------------
Create your library (by default, goes to '~/.pubs/').

    pubs init

Import existing data from bibtex (pubs will try to automatically copy documents defined as 'file' in bibtex):

    pubs import path/to/collection.bib

or for a .bib file containing a single reference:

    pubs add reference.bib -d article.pdf

pubs can also automatically retrieve the bibtex from a doi:

    pubs add -D 10.1007/s00422-012-0514-6

or an ISBN (dashes are ignored):

    pubs add -I 978-0822324669

The pdfs must still be downloaded manually.


References always up-to-date
----------------------------
If you use latex, you can automatize references, by creating a bash script with:

    #!/bin/bash
    pubs export > references.bib
    latex manuscript.tex
    bibtex manuscript
    latex manuscript.tex

This ensure that your reference file is always up-to-date; you can cite a paper in your manuscript a soon as you add it in bibtex. This means that if you have, for instance, a doi on a webpage, you only need to do:

    pubs add -D 10.1007/s00422-012-0514-6

and then add `\cite{Loeb_2012}` in your manuscript. After running the bash script, the citation will correctly appear in your compiled pdf.

Requirements
------------
- python >= 2.6
- [dateutil](http://labix.org/python-dateutil)
- [pyYaml](http://pyyaml.org) (will be deprecated soon)
- [bibtexparser](https://github.com/sciunto/python-bibtexparser) >= 0.5.3


Authors
-------

 - [Fabien Benureau](http://fabien.benureau.com)
 - Olivier Mangin
 - Jonathan Grizou
