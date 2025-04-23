import keyword
import typing as ta

from .. import check
from .. import dataclasses as dc
from .. import lang


if ta.TYPE_CHECKING:
    import markupsafe as ms

    _HAS_MARKUPSAFE = True

else:
    ms = lang.proxy_import('markupsafe')

    _HAS_MARKUPSAFE = lang.can_import('markupsafe')


String: ta.TypeAlias = ta.Union[
    str,
    'ms.Markup',
]

Content: ta.TypeAlias = ta.Union[
    list['Content'],
    'Dom',
    String,
    None,
]

ContentT = ta.TypeVar('ContentT', bound=Content)


##


ATTR_NAMES_BY_KWARG: ta.Mapping[str, str] = {
    **{f'{k}_': k for k in keyword.kwlist if k == k.lower()},
}

ATTR_KWARGS_BY_NAME: ta.Mapping[str, str] = {v: k for k, v in ATTR_NAMES_BY_KWARG.items()}


def kwargs_to_attrs(**kwargs: ta.Any) -> dict[str, ta.Any]:
    return {
        ATTR_NAMES_BY_KWARG.get(k, k).replace('_', '-'): v
        for k, v in kwargs.items()
    }


##


@dc.dataclass()
class Dom:
    tag: str
    attrs: dict[str, ta.Any | None] | None = dc.xfield(None, repr_fn=lang.opt_repr)
    body: list[Content] | None = dc.xfield(None, repr_fn=lang.opt_repr)

    def set(self, **kwargs: ta.Any) -> 'Dom':
        if self.attrs is None:
            self.attrs = {}
        self.attrs.update(**kwargs_to_attrs(**kwargs))
        return self

    def unset(self, *keys: str) -> 'Dom':
        if self.attrs is not None:
            for k in keys:
                self.attrs.pop(k, None)
        return self

    def add(self, *contents: Content) -> 'Dom':
        if self.body is None:
            self.body = []
        for c in contents:
            check_content(c)
        self.body.extend(contents)
        return self

    def remove(self, *contents: Content, strict: bool = False) -> 'Dom':
        if self.body is not None:
            i = 0
            while i < len(self.body):
                e = self.body[i]
                if any(c is e for c in contents):
                    del self.body[i]
                elif strict:
                    raise ValueError(f'Content {e} not in body')
                else:
                    i += 1
        return self


##


STRING_TYPES: tuple[type, ...] = (
    str,
    *([ms.Markup] if _HAS_MARKUPSAFE else []),
)

CONTENT_TYPES: tuple[type, ...] = (
    list,
    Dom,
    *STRING_TYPES,
    type(None),
)


def check_content(c: ContentT) -> ContentT:
    if isinstance(c, list):
        for e in c:
            check_content(e)
    else:
        check.isinstance(c, CONTENT_TYPES)
    return c


def iter_content(c: Content) -> ta.Iterator[Dom | String]:
    if isinstance(c, list):
        for e in c:
            yield from iter_content(e)
    elif isinstance(c, (Dom, *STRING_TYPES)):
        yield c  # type: ignore[misc]
    elif c is None:
        pass
    else:
        raise TypeError(c)
