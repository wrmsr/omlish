import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import dispatch
from omlish.text import templating as tpl

from ..namespaces import ContentNamespace
from ..placeholders import ContentPlaceholder
from ..placeholders import PlaceholderContent
from ..types import BaseContent
from ..types import Content
from .base import ContentTransform


##


PlaceholderContentKey: ta.TypeAlias = str | type[ContentPlaceholder]
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


class ContentDepthExceededError(Exception):
    pass


class ContentMaterializer(ContentTransform):
    DEFAULT_MAX_DEPTH: int = 100

    def __init__(
            self,
            *,
            placeholder_contents: PlaceholderContents | None = None,
            templater_context: tpl.Templater.Context | None = None,
            max_depth: int = DEFAULT_MAX_DEPTH,
    ) -> None:
        super().__init__()

        self._templater_context = templater_context
        self._placeholder_content_fn = _make_placeholder_content_fn(placeholder_contents)
        self._max_depth = max_depth

        self._cur_depth = 0

    def materialize(self, o: Content) -> Content:
        if self._cur_depth >= self._max_depth:
            raise ContentDepthExceededError

        self._cur_depth += 1
        try:
            return self._materialize(o)
        finally:
            self._cur_depth -= 1

    @dispatch.method()
    def _materialize(self, o: Content) -> Content:
        raise TypeError(o)

    #

    @_materialize.register
    def _materialize_str(self, o: str) -> Content:
        return o

    @_materialize.register
    def _materialize_base_content(self, o: BaseContent) -> Content:
        return o

    #

    @_materialize.register
    def _materialize_iterable(self, o: ta.Iterable) -> Content:
        # `collections.abc.Iterable` appears as a virtual base in the dispatch c3.mro for ContentNamespace before `type`
        # does (due to NamespaceMeta having `__iter__`), so handle that here too.
        if isinstance(o, type) and issubclass(o, ContentNamespace):
            return self._materialize_namespace_type(o)

        else:
            return [self.materialize(e) for e in o]

    @_materialize.register
    def _materialize_none(self, o: None) -> Content:
        return []

    #

    @_materialize.register
    def _materialize_placeholder(self, o: PlaceholderContent) -> Content:
        return self.materialize(self._placeholder_content_fn(o))

    def _materialize_placeholder_marker_type(self, o: type[ContentPlaceholder]) -> Content:
        check.issubclass(o, ContentPlaceholder)
        return self.materialize(self._placeholder_content_fn(o))

    #

    def _materialize_namespace_type(self, o: type[ContentNamespace]) -> Content:
        check.issubclass(o, ContentNamespace)

        out: list[Content] = []
        for n, e in o:
            if n.startswith('_'):
                continue
            out.append(self.materialize(e))
        return out

    #

    @_materialize.register
    def _materialize_type(self, o: type) -> Content:
        if issubclass(o, ContentPlaceholder):
            return self._materialize_placeholder_marker_type(o)

        elif issubclass(o, ContentNamespace):
            return self._materialize_namespace_type(o)

        else:
            raise TypeError(o)

    #

    @_materialize.register
    def _materialize_templater(self, o: tpl.Templater) -> Content:
        return o.render(check.not_none(self._templater_context))


def materialize_content(
        o: Content,
        *,
        placeholder_contents: PlaceholderContents | None = None,
        templater_context: tpl.Templater.Context | None = None,
) -> Content:
    return ContentMaterializer(
        placeholder_contents=placeholder_contents,
        templater_context=templater_context,
    ).materialize(o)
