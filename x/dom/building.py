import typing as ta

from omlish import dataclasses as dc

from .content import Content
from .content import kwargs_to_attrs
from .content import Dom


##


def d(
        tag: str,
        *attrs_and_contents: tuple[str, ta.Any] | Content,
        **kwargs: ta.Any,
) -> Dom:
    c = []
    for a in attrs_and_contents:
        if isinstance(a, tuple):
            k, v = a
            if k in kwargs:
                raise KeyError(f'Attribute {k} already set')
            kwargs[k] = v
        else:
            c.append(a)

    return Dom(
        tag,
        attrs=kwargs_to_attrs(**kwargs) or None,
        body=c or None,
    )


##


@dc.dataclass(frozen=True)
class DomBuilder:
    tag: str

    def __call__(
            self,
            *attrs_and_contents: tuple[str, ta.Any] | Content,
            **kwargs: ta.Any,
    ) -> Dom:
        return d(self.tag, *attrs_and_contents, **kwargs)


class DomAccessor:
    def __getattr__(self, tag: str) -> DomBuilder:
        return DomBuilder(tag)


D = DomAccessor()
