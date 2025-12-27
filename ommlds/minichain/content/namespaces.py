from omlish import dataclasses as dc
from omlish import lang

from .dynamic import DynamicContent
from .types import LeafContent


##


class ContentNamespace(lang.Namespace, lang.Abstract):
    pass


@dc.dataclass(frozen=True)
class NamespaceContent(DynamicContent, LeafContent, lang.Final):
    ns: type[ContentNamespace]
