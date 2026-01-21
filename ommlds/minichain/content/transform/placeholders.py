import typing as ta

from omlish import dataclasses as dc

from ..content import Content
from ..placeholders import PlaceholderContent
from ..placeholders import PlaceholderContentKey
from .visitors import VisitorContentTransform


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


class PlaceholderContentMaterializer(VisitorContentTransform[None]):
    def __init__(
            self,
            placeholder_contents: PlaceholderContents | None = None,
    ) -> None:
        super().__init__()

        self._placeholder_content_fn = _make_placeholder_content_fn(placeholder_contents)

    def visit_placeholder_content(self, c: PlaceholderContent, ctx: None) -> Content:
        return self._placeholder_content_fn(c.k)
