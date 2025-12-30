import typing as ta

from omlish import check
from omlish import dataclasses as dc

from ..namespaces import ContentNamespace
from ..namespaces import NamespaceContent
from ..placeholders import PlaceholderContent
from ..placeholders import PlaceholderContentKey
from ..recursive import RecursiveContent
from ..types import Content
from .base import ContentTransform


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


class RecursiveContentMaterializer(ContentTransform):
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

    def recurse(self, o: Content) -> Content:
        if self._cur_depth >= self._max_depth:
            raise RecursiveContentDepthExceededError

        self._cur_depth += 1
        try:
            return self.apply(o)
        finally:
            self._cur_depth -= 1

    @ContentTransform.apply.register
    def apply_recursive_content(self, c: RecursiveContent) -> Content:
        raise TypeError(c)

    @ContentTransform.apply.register
    def apply_namespace_content(self, c: NamespaceContent) -> Content:
        check.issubclass(c.ns, ContentNamespace)
        out: list[Content] = []
        for n, e in c.ns:
            if n.startswith('_'):
                continue
            out.append(self.recurse(e))
        return out

    @ContentTransform.apply.register
    def apply_placeholder_content(self, c: PlaceholderContent) -> Content:
        return self.recurse(self._placeholder_content_fn(c.k))
