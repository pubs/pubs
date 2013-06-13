Papers brings your bibliography to the command line.

Papers organizes your bibliographic documents together with the bibliographic data associated to them and provides command line access to basic and advanced manipulation of your library.

Papers is built with the following principles in mind:

 - all papers are referenced using unique citation keys,
 - bibliographic data (i.e. pure bibtex information) is kept separated from metadata (including links to pdf or tags),
 - everything is stored in plain text so it can be manually edited or version controlled.


Notice: papers is still in early development and cannot be considered as stable


Getting started
---------------
Create your library (by default, goes to '~/.papers/').

    papers init

Import existing data from bibtex (papers will try to automatically copy documents defined as 'file' in bibtex):

    papers import path/to/collection.bib
or for bibtex containing a single file:

    papers add --bibfile article.bib --docfile article.pdf


Authors
-------

 - Fabien Benureau
 - Olivier Mangin
 - Jonathan Grizou
