from omlish import dataclasses as dc
from omlish import lang

from .content import LeafContent
from .dynamic import DynamicContent


##


class ContentNamespace(lang.Namespace, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class NamespaceContent(DynamicContent, LeafContent, lang.Final):
    ns: type[ContentNamespace]
