import dataclasses as dc


@dc.dataclass(frozen=True)
class Baz:
    i: int
    s: str


@dc.dataclass(frozen=True)
class Bar:
    baz: Baz


@dc.dataclass(frozen=True)
class Foo:
    bar: Bar


def _main() -> None:
    f0 = Foo(Bar(Baz(0, 'a')))
    print(f0)

    f1 = dc.replace(f0, bar=dc.replace(f0.bar, baz=dc.replace(f0.bar.baz, i=f0.bar.baz.i + 1)))
    print(f1)


if __name__ == '__main__':
    _main()
