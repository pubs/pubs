# Function here may belong somewhere else. In the mean time...

def resolve_citekey(repo, citekey, ui=None, exit_on_fail=True):
    """Check that a citekey exists, or autocompletes it if not ambiguous."""
    # FIXME. Make me optionally non ui interactive/exiting
    citekeys = repo.citekeys_from_prefix(citekey)
    if len(citekeys) == 0:
        if ui is not None:
            ui.error("No citekey named or beginning with '{}".format(citekey))
            if exit_on_fail:
                ui.exit()
    elif len(citekeys) == 1:
        if citekeys[0] != citekey:
            if ui is not None:
                ui.print_("Provided citekey '{}' has been autocompleted into '{}'".format(citekey, citekeys[0]))
            citekey = citekeys[0]
    elif citekey not in citekeys:
        if ui is not None:
            ui.error("Be more specific. Provided citekey '{}' matches multiples citekeys: {}".format(citekey, ', '.join(citekeys)))
            if exit_on_fail:
                ui.exit()
    return citekey


