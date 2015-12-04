from .. import __version__

configspec = """
[main]

# Where the pubs repository files (bibtex, metadata, notes) are located
pubsdir = string(default='~/pubs')

# Where the documents files are located (default: $(pubsdir)/doc/)
docsdir = string(default="docsdir://")

# Specify if a document should be copied or moved in the docdir, or only
# linked when adding a publication.
doc_add = option('copy', 'move', 'link', default='move')

# if True, pubs will ask confirmation before copying/moving/linking the
# document file.
doc_add_ask = boolean(default=True)

# the command to use when opening document files
open_cmd = string(default=None)

# which editor to use when editing bibtex files.
# if using a graphical editor, use the --wait or --block option, i.e.:
# "atom --wait"
# "kate --block"
edit_cmd = string(default=None)


[formating]

# Enable bold formatting, if the terminal supports it.
bold    = boolean(default=True)

# Enable italics, if the terminal supports it.
italics = boolean(default=True)

# Enable colors, if the terminal supports it.
color = boolean(default=True)


[theme]




[plugins]
# comma-separated list of the plugins to load
active = list(default=list())

[internal]
# The version of this configuration file. Do not edit.
version = string(min=5, default='{}')

""".format(__version__).split('\n')
