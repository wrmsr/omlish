import typing as ta

from omlish import check
from omlish import dataclasses as dc

from ..content import Content
from ..namespaces import ContentNamespace
from ..namespaces import NamespaceContent
from ..placeholders import PlaceholderContent
from ..placeholders import PlaceholderContentKey
from ..recursive import RecursiveContent
from ..visitors import ContentTransform


##


PlaceholderContentMap: ta.TypeAlias = ta.Mapping[PlaceholderContentKey, Content]
PlaceholderContentFn: ta.TypeAlias = ta.Callable[[PlaceholderContentKey], Content]
PlaceholderContents: ta.TypeAlias = PlaceholderContentMap | PlaceholderContentFn


@dc.dataclass()
class PlaceholderContentMissingError(Exception):
    key: PlaceholderContentKey


def _make_placeholder_content_fn(cps: PlaceholderContents | None = None) -> PlaceholderContentFn:
    if cps is None:
        def none_fn(cpk: PlaceholderContentKey) -> Content:
            raise PlaceholderContentMissingError(cpk)

        return none_fn

    elif isinstance(cps, ta.Mapping):
        def mapping_fn(cpk: PlaceholderContentKey) -> Content:
            try:
                return cps[cpk]
            except KeyError:
                raise PlaceholderContentMissingError(cpk) from None

        return mapping_fn

    elif callable(cps):
        return cps

    else:
        raise TypeError(cps)


##


class RecursiveContentDepthExceededError(Exception):
    pass


class RecursiveContentMaterializer(ContentTransform[None]):
    DEFAULT_MAX_DEPTH: int = 8

    def __init__(
            self,
            placeholder_contents: PlaceholderContents | None = None,
            *,
            max_depth: int = DEFAULT_MAX_DEPTH,
    ) -> None:
        super().__init__()

        self._placeholder_content_fn = _make_placeholder_content_fn(placeholder_contents)
        self._max_depth = max_depth

        self._cur_depth = 0

    def recurse(self, o: Content, ctx: None) -> Content:
        if self._cur_depth >= self._max_depth:
            raise RecursiveContentDepthExceededError

        self._cur_depth += 1
        try:
            return self.visit(o, ctx)
        finally:
            self._cur_depth -= 1

    def visit_recursive_content(self, c: RecursiveContent, ctx: None) -> Content:
        raise TypeError(c)

    def visit_namespace_content(self, c: NamespaceContent, ctx: None) -> Content:
        check.issubclass(c.ns, ContentNamespace)
        out: list[Content] = []
        for n, e in c.ns:
            if n.startswith('_'):
                continue
            out.append(self.recurse(e, ctx))
        return out

    def visit_placeholder_content(self, c: PlaceholderContent, ctx: None) -> Content:
        return self.recurse(self._placeholder_content_fn(c.k), ctx)
