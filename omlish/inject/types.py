import collections

from .. import lang


##


Tag = collections.namedtuple('Tag', 'tag')  # noqa


class Scope(lang.Abstract):
    def __repr__(self) -> str:
        return type(self).__name__


class Unscoped(Scope, lang.Singleton, lang.Final):
    pass
