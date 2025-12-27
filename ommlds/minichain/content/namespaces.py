from omlish import lang

from .dynamic import DynamicContent


##


class ContentNamespace(lang.Namespace, lang.Abstract):
    pass



class NamespaceContent(DynamicContent, lang.Final):
    ns: type[ContentNamespace]
