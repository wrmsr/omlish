import abc
import dataclasses as dc
import typing as ta


T = ta.TypeVar('T')


##


class Request(abc.ABC):  # noqa
    pass


@dc.dataclass()
class Task:
    req: Request
    done = False
    res = None

    def __await__(self):
        if not self.done:
            yield self
        if not self.done:
            raise RuntimeError("await wasn't used with task")
        return self.res


##


@dc.dataclass(frozen=True)
class FrobRequest(Request, ta.Generic[T]):
    v: T


async def frob(v: T) -> ta.Any:
    return await Task(FrobRequest(v))


async def foo():
    a1 = await frob(1)
    print(f'a1: {a1}')
    a2 = await frob(2)
    print(f'a1: {a2}')
    return 3


def _main():
    g = foo().__await__()
    gi = iter(g)
    while True:
        try:
            t = gi.__next__()
        except StopIteration as e:
            print(f'r: {e.value}')
            break
        else:
            print(f't: {t}')
            if isinstance(t.req, FrobRequest):
                t.done = True
                t.res = f'frobbed: {t.req.v}'
            else:
                raise TypeError(t.req)


if __name__ == '__main__':
    _main()
