import typing as ta

from ... import dataclasses as dc
from ..impl.inspect import signature


@dc.dataclass(frozen=True)
class Tag:
    tag: ta.Any = dc.xfield(check=lambda o: not isinstance(o, Tag))


def test_tags():
    def f(a: ta.Annotated[int, Tag(420)]):
        pass

    s = signature(f)
    print(s)
