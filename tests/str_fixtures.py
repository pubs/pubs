from __future__ import unicode_literals


bibtex_external0 = """
@techreport{Page99,
     number = {1999-66},
      month = {November},
     author = {Lawrence Page and Sergey Brin and Rajeev Motwani and Terry Winograd},
       note = {Previous number = SIDL-WP-1999-0120},
      title = {The PageRank Citation Ranking: Bringing Order to the Web.},
       type = {Technical Report},
  publisher = {Stanford InfoLab},
       year = {1999},
institution = {Stanford InfoLab},
        url = {http://ilpubs.stanford.edu:8090/422/},
   abstract = "The importance of a Web page is an inherently subjective matter, which depends on the readers interests, knowledge and attitudes. But there is still much that can be said objectively about the relative importance of Web pages. This paper describes PageRank, a mathod for rating Web pages objectively and mechanically, effectively measuring the human interest and attention devoted to them. We compare PageRank to an idealized random Web surfer. We show how to efficiently compute PageRank for large numbers of pages. And, we show how to apply PageRank to search and to user navigation.",
}
"""

bibtex_external_alt = """
@techreport{Page99,
     number = {1999-66},
      month = {November},
     author = {Lawrence Page and Sergey Brin and Rajeev Motwani and Terry Winograd},
       note = {Previous number = SIDL-WP-1999-0120},
      title = {The PageRank Citation Ranking: Bringing Order to the Web.},
       type = {Technical Report},
  publisher = {Stanford InfoLab},
       year = {9999},
institution = {Stanford InfoLab},
        url = {http://ilpubs.stanford.edu:8090/422/},
   abstract = "This is not a real entry, it is just here to test overwriting fails on import. it must have a different year than the str_fixture bibtex_external0, but must have the same citekey for the test to be valid.",
}
"""

bibtex_raw0 = """@techreport{
    Page99,
    author = "Page, Lawrence and Brin, Sergey and Motwani, Rajeev and Winograd, Terry",
    publisher = "Stanford InfoLab",
    title = "The PageRank Citation Ranking: Bringing Order to the Web.",
    url = "http://ilpubs.stanford.edu:8090/422/",
    abstract = "The importance of a Web page is an inherently subjective matter, which depends on the readers interests, knowledge and attitudes. But there is still much that can be said objectively about the relative importance of Web pages. This paper describes PageRank, a mathod for rating Web pages objectively and mechanically, effectively measuring the human interest and attention devoted to them. We compare PageRank to an idealized random Web surfer. We show how to efficiently compute PageRank for large numbers of pages. And, we show how to apply PageRank to search and to user navigation.",
    number = "1999-66",
    month = "November",
    note = "Previous number = SIDL-WP-1999-0120",
    year = "1999",
    type = "Technical Report",
    institution = "Stanford InfoLab",
}

"""

metadata_raw0 = """docfile: docsdir://Page99.pdf
tags: [search, network]
added: '2013-11-14 13:14:20'
"""

turing_bib = """@article{turing1950computing,
  title={Computing machinery and intelligence},
  author={Turing, Alan M},
  journal={Mind},
  editor={Edward A. Feigenbaum and Julian Feldman},
  volume={59},
  number={236},
  pages={433--460},
  year={1950},
  publisher={JSTOR}
}

"""

turing_meta = """\
tags: [AI, computer]
added: '2013-11-14 13:14:20'
"""

# Should not parse (see #113)
bibtex_no_citekey = """@Manual{,
    title = {R: A Language and Environment for Statistical Computing},
    author = {{R Core Team}},
    organization = {R Foundation for Statistical Computing},
    address = {Vienna, Austria},
    year = {2017},
    url = {https://www.R-project.org/},
}
"""

bibtex_month = """@inproceedings{Goyal2017,
 author = {Goyal, Anirudh and Sordoni, Alessandro and C{\^{o}}t{\'{e}}, Marc-Alexandre and Ke, Nan Rosemary and Bengio, Yoshua},
 title = {Z-Forcing: Training Stochastic Recurrent Networks},
 year = {2017},
 month = dec,
 pages = {6716--6726},
}
"""

not_bibtex = """@misc{this looks,
  like = a = bibtex file but
    , is not a real one!

"""

bibtex_with_latex = """@article{kjaer2018large,
  title={A large impact crater beneath Hiawatha Glacier in northwest Greenland},
  author={Kj{\\ae}r, Kurt H and Larsen, Nicolaj K and Binder, Tobias and Bj{\\o}rk, Anders A and Eisen, Olaf and Fahnestock, Mark A and Funder, Svend and Garde, Adam A and Haack, Henning and Helm, Veit and others},
  journal={Science advances},
  volume={4},
  number={11},
  pages={eaar8173},
  year={2018},
  publisher={American Association for the Advancement of Science}
}
"""

sample_conf = """
[main]

# Where the pubs repository files (bibtex, metadata, notes) are located
pubsdir = /Users/fabien/research/renc/.pubs

# Where the documents files are located (default: $(pubsdir)/doc/)
docsdir = /Users/fabien/Dropbox/research/pubsdoc

# Specify if a document should be copied or moved in the docdir, or only
# linked when adding a publication.
doc_add = move

# the command to use when opening document files
open_cmd = open

# which editor to use when editing bibtex files.
# if using a graphical editor, use the --wait or --block option, i.e.:
# "atom --wait"
# "kate --block"
edit_cmd = "vim"

# If true debug mode is on which means exceptions are not catched and
# the full python stack is printed.
debug = False

[formating]

# Enable bold formatting, if the terminal supports it.
bold = False

# Enable italics, if the terminal supports it.
italics = False

# Enable colors, if the terminal supports it.
color = False


[theme]

# Here you can define the color theme used by pubs, if enabled in the
# 'formating' section. Predefined theme are available at:
# https://github.com/pubs/pubs/blob/master/extra/themes.md


[plugins]
# Comma-separated list of the plugins to load.
# The only current available plugin is alias.
active = alias,

[[alias]]
# new subcommands can be defined, e.g.:
# print = open --with lp
# evince = open --with evince
open = doc open

# shell commands can also be defined, by prefixing them with a bang `!`, e.g:
# count = !pubs list -k | wc -l

[internal]
# The version of this configuration file. Do not edit.
version = 0.6.0
"""
