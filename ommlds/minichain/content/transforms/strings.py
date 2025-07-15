import typing as ta

from omlish import dataclasses as dc

from .base import ContentTransform


T = ta.TypeVar('T')


##


@dc.dataclass(frozen=True)
class StringFnContentTransform(ContentTransform):
    fn: ta.Callable[[str], str]

    @ContentTransform.apply.register  # noqa
    def apply_str(self, s: str) -> str:
        return self.fn(s)


def transform_content_strings(fn: ta.Callable[[str], str], o: T) -> T:
    return StringFnContentTransform(fn).apply(o)
