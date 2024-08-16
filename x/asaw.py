import dataclasses as dc
import typing as ta


T = ta.TypeVar('T')


@dc.dataclass(frozen=True)
class ValueAwaitable(ta.Generic[T]):
    v: T

    def __await__(self):
        yield self.v


async def foo():
    await ValueAwaitable(1)
    await ValueAwaitable(2)
    return 3


def _main():
    g = foo().__await__()
    gi = iter(g)
    while True:
        try:
            gv = next(gi)
        except StopIteration as e:
            print(f'r: {e.value}')
            break
        else:
            print(f'i: {gv}')


if __name__ == '__main__':
    _main()
