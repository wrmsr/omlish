from omlish import dataclasses as dc
from omlish import lang

from .dynamic import DynamicContent


##


class ContentNamespace(lang.Namespace, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class NamespaceContent(DynamicContent, lang.Final):
    ns: type[ContentNamespace]
