## Color Themes

Here are some color themes for pubs. Copy-paste them in your configuration
under the [theme] section (while deleting or commenting the current theme).

Some of those theme require 256 colors. You can see which color correspond
to which code by executing the `colors.sh` script in the `extra` folder in
your terminal.  


### Color titles

For light and dark backgrounds.
You can modify the title color to suit your taste. Current value is dark red.
```
# messages
ok       = 'green'
warning  = '166'
error    = 'bred'

# ui elements
filepath = 'bold'
citekey  = ''
tag      = ''

# bibliographic fields
author    = 'bold'
title     = '124'
publisher = ''
year      = ''
volume    = ''
pages     = ''
```

### Light grey

For dark backgrounds.

```
[theme]
# messages
ok       = '240'
warning  = '240'
error    = 'b240'

# ui elements
filepath = 'bold'
citekey  = 'b250'
tag      = '240'

# bibliographic fields
author    = 'b240'
title     = '245'
publisher = 'i240'
year      = '252'
volume    = '240'
pages     = '240'
```
