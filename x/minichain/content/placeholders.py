import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ..content.content import Content
from .recursive import RecursiveContent


##


class ContentPlaceholder(lang.Marker, lang.Abstract):
    pass


PlaceholderContentKey: ta.TypeAlias = str | type[ContentPlaceholder]


@dc.dataclass(frozen=True)
@dc.extra_class_params(terse_repr=True)
class PlaceholderContent(RecursiveContent, lang.Final):
    k: PlaceholderContentKey


##


PlaceholderContentValue: ta.TypeAlias = Content | ta.Callable[[], Content]
PlaceholderContentMap: ta.TypeAlias = ta.Mapping[PlaceholderContentKey, PlaceholderContentValue]

PlaceholderContents: ta.TypeAlias = ta.Union[  # noqa
    PlaceholderContentMap,
    ta.Iterable['PlaceholderContents'],
    ta.Callable[[], 'PlaceholderContents'],
]
