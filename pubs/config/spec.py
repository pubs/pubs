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

# Here you can define the color theme used by pubs, if enabled in the
# 'formating' section. Predefined theme are available at:
# https://github.com/pubs/pubs/blob/master/theme.md

# Available colors are: 'black', 'red', 'green', 'yellow', 'blue', 'purple',
# 'cyan', and 'grey'. Bold colors are available by prefixing 'b' in front of
# the color name ('bblack', 'bred', etc.), italic colors by prefixing 'i',
# and bold italic by prefixing 'bi'. Finally, 'bold', 'italic' and
# 'bolditalic' can be used to apply formatting without changing the color.
# For no color, use an empty string ''

# messages
ok       = string(default='green')
warning  = string(default='yellow')
error    = string(default='red')

# ui elements
filepath = string(default='bold')
citekey  = string(default='purple')
tag      = string(default='cyan')

# bibliographic fields
author    = string(default='bold')
title     = string(default='')
publisher = string(default='italic')
year      = string(default='bold')
volume    = string(default='bold')
pages     = string(default='')


[plugins]
# comma-separated list of the plugins to load
active = list(default=list())

[internal]
# The version of this configuration file. Do not edit.
version = string(min=5, default='{}')

""".format(__version__).split('\n')