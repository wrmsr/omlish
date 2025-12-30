from omlish import dataclasses as dc
from omlish import lang

from .recursive import RecursiveContent


##


class ContentNamespace(lang.Namespace, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class NamespaceContent(RecursiveContent, lang.Final):
    ns: type[ContentNamespace]
