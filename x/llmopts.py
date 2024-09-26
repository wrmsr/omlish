import dataclasses as dc
import typing as ta

from omlish import lang


T = ta.TypeVar('T')


@dc.dataclass(frozen=True)
class Option(ta.Generic[T], lang.Abstract):
    v: T


@dc.dataclass(frozen=True)
class TopK(Option[int], lang.Final):
    pass


@dc.dataclass(frozen=True)
class Temperature(Option[float], lang.Final):
    pass


def generate(prompt: str, *options: Option) -> None:
    print(options)


def _main() -> None:
    generate('foo', TopK(1))
    generate('foo', Temperature(.1))
    generate('foo', TopK(1), Temperature(.1))


if __name__ == '__main__':
    _main()
