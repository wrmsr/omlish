import dataclasses as dc
import typing as ta


T = ta.TypeVar('T')


@dc.dataclass(frozen=True)
class ValueAwaitable(ta.Generic[T]):
    v: T



async def foo():
    await 1
    await 2
    return 3


def _main():
    g = foo().__await__()
    for o in g:
        print(o)


if __name__ == '__main__':
    _main()
