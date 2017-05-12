from . import repo
try:
    import argcomplete
except ModuleNotFoundError:

    class FakeModule:

        @staticmethod
        def _fun(**kwargs):
            pass

        def __getattr__(self, _):
            return self._fun

    argcomplete = FakeModule()


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
