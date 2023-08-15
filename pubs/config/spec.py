from .. import __version__

configspec = """
[main]

# Where the pubs repository files (bibtex, metadata, notes) are located
pubsdir = string(default='~/pubs')

# Where the documents files are located (default: $(pubsdir)/doc/)
docsdir = string(default="docsdir://")

# Specify if a document should be copied or moved in the docdir, or only
# linked when adding a publication.
doc_add = option('copy', 'move', 'link', default='copy')

# the command to use when opening document files
open_cmd = string(default=None)

# which editor to use when editing bibtex files.
# if using a graphical editor, use the --wait or --block option, i.e.:
# "atom --wait"
# "kate --block"
# If set to an empty string (default) pubs uses the value of the environment
# variable $EDITOR.
edit_cmd = string(default='')

# Which default extension to use when creating a note file.
note_extension = string(default='txt')

# How many authors to display when displaying a citation. If there are more
# authors, only the first author is diplayed followed by 'et al.'.
max_authors = integer(default=3)

# If true debug mode is on which means exceptions are not catched and
# the full python stack is printed.
debug = boolean(default=False)

# If true the citekey is normalized using the 'citekey_format' on adding new publications.
normalize_citekey = boolean(default=False)

# String specifying how to format the citekey. All strings of
# the form '{{substitution:modifier}}' and '{{substitution}}' will
# be substituted with their appropriate values. The following
# substitutions are used:
#    author_last_name: last name of the first author
#    year: year of publication
#    short_title: first word of the title (excluding words such as "the", "an", ...)
# modifiers:
#    l: converts the text to lowercase
#    u: converts the text to uppercase
# examples:
#   {{author_last_name:l}}{{year}} generates 'yang2020'
#   {{author_last_name}}{{year}}{{short_title}} generates 'Yang2020Towards'
#   {{author_last_name:l}}{{year}}{{short_title:l}} generates 'yang2020towards'
#   {{author_last_name:u}}{{year}} generates 'YANG2020'
#
citekey_format = string(default='{{author_last_name:l}}{{year}}{{short_title:l}}')

# which bibliographic fields to exclude from bibtex files. By default, none.
# Please note that excluding critical fields such as `title` or `author`
# will break many commands of pubs.
exclude_bibtex_fields = force_list(default=list())

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
# https://github.com/pubs/pubs/blob/master/extra/themes.md

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
publisher = string(default='')
year      = string(default='bold')
volume    = string(default='bold')
pages     = string(default='')


[plugins]
# Comma-separated list of the plugins to load.
# Currently pubs comes with built-in plugins alias and git.
active = force_list(default=list('alias'))

[[alias]]
# new subcommands can be defined, e.g.:
# print = open --with lp
# evince = open --with evince

# shell commands can also be defined, by prefixing them with a bang `!`, e.g:
# count = !pubs list -k | wc -l

# aliases can also be defined with descriptions using the following configobj
# subsectioning.  NOTE: any aliases defined this way should come after all other
# aliases, otherwise simple aliases will be ignored.
# [[[count]]]
# command = !pubs list -k | wc -l
# description = lists number of pubs in repo

# To use commas in the description, wrap them in a "" string. For example:
# description = "lists number of pubs in repo, greets the user afterward"

[[git]]
# The git plugin will commit changes to the repository in a git repository
# created at the root of the pubs directory. All detected changes will be
# commited every time a change is made by a pubs command.
# The plugin also propose the `pubs git` subcommand, to directly send git
# commands to the pubs repository. Therefore, `pubs git status` is equivalent
# to `git -C <pubsdir> status`, with the `-C` flag instructing
# to invoke git as if the current directory was <pubsdir>. Note that a
# limitation of the subcommand is that you cannot use git commands with the
# `-c` option (pubs will interpret it first.)

# if False, will display git output when automatic commit are made.
# Invocation of `pubs git` will always have output displayed.
quiet = boolean(default=True)
# if True, git will not automatically commit changes
manual = boolean(default=False)
# if True, color will be conserved from git output (this add `-c color:always`
# to the git invocation).
force_color = boolean(default=True)


[internal]
# The version of this configuration file. Do not edit.
version = string(min=5, default='{}')

""".format(__version__).split('\n')
