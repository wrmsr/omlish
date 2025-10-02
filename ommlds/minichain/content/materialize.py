"""
TODO:
 - ExtendedCanContent
"""
import dataclasses as dc
import typing as ta

from omlish import check
from omlish import dispatch
from omlish.text import templating as tpl

from .namespaces import ContentNamespace
from .placeholders import ContentPlaceholder
from .placeholders import ContentPlaceholderMarker
from .types import Content
from .types import ExtendedContent


##


_InnerCanContent: ta.TypeAlias = ta.Union[  # noqa
    str,
    ExtendedContent,

    ContentPlaceholder,
    type[ContentPlaceholderMarker],

    type[ContentNamespace],

    tpl.Templater,
]

CanContent: ta.TypeAlias = ta.Union[  # noqa
    ta.Iterable['CanContent'],

    None,

    _InnerCanContent,
]


##


ContentPlaceholderKey: ta.TypeAlias = ContentPlaceholder | type[ContentPlaceholderMarker]
ContentPlaceholderMap: ta.TypeAlias = ta.Mapping[ContentPlaceholderKey, CanContent]
ContentPlaceholderFn: ta.TypeAlias = ta.Callable[[ContentPlaceholderKey], CanContent]
ContentPlaceholders: ta.TypeAlias = ContentPlaceholderMap | ContentPlaceholderFn


@dc.dataclass()
class ContentPlaceholderMissingError(Exception):
    key: ContentPlaceholderKey


def _make_content_placeholder_fn(cps: ContentPlaceholders | None = None) -> ContentPlaceholderFn:
    if cps is None:
        def none_fn(cpk: ContentPlaceholderKey) -> CanContent:
            raise ContentPlaceholderMissingError(cpk)

        return none_fn

    elif isinstance(cps, ta.Mapping):
        def mapping_fn(cpk: ContentPlaceholderKey) -> CanContent:
            try:
                return cps[cpk]
            except KeyError:
                raise ContentPlaceholderMissingError(cpk) from None

        return mapping_fn

    elif callable(cps):
        return cps

    else:
        raise TypeError(cps)


##


class ContentDepthExceededError(Exception):
    pass


class ContentMaterializer:
    DEFAULT_MAX_DEPTH: int = 100

    def __init__(
            self,
            *,
            content_placeholders: ContentPlaceholders | None = None,
            templater_context: tpl.Templater.Context | None = None,
            max_depth: int = DEFAULT_MAX_DEPTH,
    ) -> None:
        super().__init__()

        self._templater_context = templater_context
        self._content_placeholders_fn = _make_content_placeholder_fn(content_placeholders)
        self._max_depth = max_depth

        self._cur_depth = 0

    def materialize(self, o: CanContent) -> Content:
        if self._cur_depth >= self._max_depth:
            raise ContentDepthExceededError

        self._cur_depth += 1
        try:
            return self._materialize(o)
        finally:
            self._cur_depth -= 1

    @dispatch.method()
    def _materialize(self, o: CanContent) -> Content:
        raise TypeError(o)

    #

    @_materialize.register
    def _materialize_str(self, o: str) -> Content:
        return o

    @_materialize.register
    def _materialize_extended_content(self, o: ExtendedContent) -> Content:
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
    def _materialize_placeholder(self, o: ContentPlaceholder) -> Content:
        return self.materialize(self._content_placeholders_fn(o))

    def _materialize_placeholder_marker_type(self, o: type[ContentPlaceholderMarker]) -> Content:
        check.issubclass(o, ContentPlaceholderMarker)
        return self.materialize(self._content_placeholders_fn(o))

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
        if issubclass(o, ContentPlaceholderMarker):
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
        o: CanContent,
        *,
        content_placeholders: ContentPlaceholders | None = None,
        templater_context: tpl.Templater.Context | None = None,
) -> Content:
    return ContentMaterializer(
        content_placeholders=content_placeholders,
        templater_context=templater_context,
    ).materialize(o)
