import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ...content import Content
from ...placeholders import PlaceholderContent
from ...placeholders import PlaceholderContentKey
from ...placeholders import PlaceholderContentMap
from ...placeholders import PlaceholderContents
from ..visitors import VisitorContentTransform


##


@dc.dataclass()
class PlaceholderContentKeyError(Exception):
    key: PlaceholderContentKey


class MissingPlaceholderContentKeyError(PlaceholderContentKeyError):
    pass


class DuplicatePlaceholderContentKeyError(PlaceholderContentKeyError):
    pass


##


class PlaceholderContentMaterializer(VisitorContentTransform):
    def __init__(
            self,
            placeholder_contents: PlaceholderContents | None = None,
    ) -> None:
        super().__init__()

        self._placeholder_contents = placeholder_contents

        self._cache: dict[PlaceholderContentKey, Content] = {}

    @lang.cached_function
    def _build_map(self) -> PlaceholderContentMap:
        dct: dict[PlaceholderContentKey, Content] = {}

        def rec(cur: PlaceholderContents) -> None:
            if callable(cur):
                rec(cur())

            elif isinstance(cur, ta.Mapping):
                for k, v in cur.items():
                    if k in dct:
                        raise DuplicatePlaceholderContentKeyError(k)

                    if callable(v):
                        v = v()

                    dct[k] = v

            else:
                for nxt in cur:
                    rec(nxt)

        if (root := self._placeholder_contents) is not None:
            rec(root)

        return dct

    def _get_placeholder_content(self, key: PlaceholderContentKey) -> Content:
        try:
            return self._cache[key]
        except KeyError:
            pass

        dct = self._build_map()
        try:
            c = dct[key]
        except KeyError:
            raise MissingPlaceholderContentKeyError(key) from None

        if callable(c):
            c = c()

        self._cache[key] = c
        return c

    def visit_placeholder_content(self, c: PlaceholderContent, ctx: None) -> Content:
        return self._get_placeholder_content(c.k)
