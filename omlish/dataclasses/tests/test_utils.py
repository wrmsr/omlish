import dataclasses as dc

from ..utils import deep_replace


@dc.dataclass(frozen=True)
class Baz:
    i: int
    s: str


@dc.dataclass(frozen=True)
class Bar:
    i: int
    baz: Baz


@dc.dataclass(frozen=True)
class Foo:
    i: int
    bar: Bar


def test_deep_replace() -> None:
    f0 = Foo(0, Bar(0, Baz(0, 'a')))
    assert deep_replace(f0, lambda foo: dict(i=foo.i + 1)) == Foo(i=1, bar=Bar(i=0, baz=Baz(i=0, s='a')))
    assert deep_replace(f0, 'bar', lambda bar: dict(i=bar.i + 1)) == Foo(i=0, bar=Bar(i=1, baz=Baz(i=0, s='a')))
    assert deep_replace(f0, 'bar', 'baz', lambda baz: dict(i=baz.i + 1)) == Foo(i=0, bar=Bar(i=0, baz=Baz(i=1, s='a')))  # noqa
