import re
try:
    import argcomplete
except ImportError:

    class FakeModule:

        @staticmethod
        def _fun(*args, **kwargs):
            pass

        def __getattr__(self, _):
            return self._fun

    argcomplete = FakeModule()

from . import repo


def autocomplete(parser):
    argcomplete.autocomplete(parser)


class BaseCompleter(object):

    def __init__(self, conf):
        self.conf = conf

    def __call__(self, **kwargs):
        try:
            return self._complete(**kwargs)
        except Exception as e:
            argcomplete.warn(e)


class CiteKeyCompletion(BaseCompleter):

    def _complete(self, **kwargs):
        rp = repo.Repository(self.conf)
        return rp.citekeys


class CiteKeyOrTagCompletion(BaseCompleter):

    def _complete(self, **kwargs):
        rp = repo.Repository(self.conf)
        return rp.citekeys.union(rp.get_tags())


class TagModifierCompletion(BaseCompleter):

    regxp = r"[^:+-]*$"  # prefix of tag after last separator

    def _complete(self, prefix, **kwargs):
        tags = repo.Repository(self.conf).get_tags()
        start, _ = re.search(self.regxp, prefix).span()
        partial_expr = prefix[:start]
        t_prefix = prefix[start:]
        return [partial_expr + t for t in tags if t.startswith(t_prefix)]


class CommaSeparatedTagsCompletion(TagModifierCompletion):

    regxp = r"[^,]*$"


class CommaSeparatedListCompletion(BaseCompleter):

    values = []

    def _complete(self, prefix, **kwargs):
        split = prefix.split(',')
        item_prefix = split[-1]
        partial = split[:-1]
        return [','.join(partial + [x]) for x in self.values
                if x.startswith(item_prefix)]
