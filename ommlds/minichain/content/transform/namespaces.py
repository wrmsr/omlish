from omlish import check

from ..content import Content
from ..namespaces import ContentNamespace
from ..namespaces import NamespaceContent
from .visitors import VisitorContentTransform


##


class NamespaceContentMaterializer(VisitorContentTransform[None]):
    def visit_namespace_content(self, c: NamespaceContent, ctx: None) -> Content:
        check.issubclass(c.ns, ContentNamespace)
        out: list[Content] = []
        for n, e in c.ns:
            if n.startswith('_'):
                continue
            out.append(self.transform(e, ctx))
        return out
