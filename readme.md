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

or for bibtex containing a single file:

    pubs add reference.bib -d article.pdf

you can also retrieve the bibtex from doi.org by giving the DOI:

    pubs add -D 10.1007/s00422-012-0514-6

The pdf must still be downloaded manually.

Requirements
------------
- python >= 2.6
- [dateutil](http://labix.org/python-dateutil)
- [pyYaml](http://pyyaml.org)
- [bibtexparser](https://github.com/sciunto/python-bibtexparser) >= 0.5.3


Authors
-------

 - [Fabien Benureau](http://fabien.benureau.com)
 - Olivier Mangin
 - Jonathan Grizou
