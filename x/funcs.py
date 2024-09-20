import abc
import operator
import typing as ta


T = ta.TypeVar('T')
U = ta.TypeVar('U')


class Func(abc.ABC, ta.Generic[T]):
    @abc.abstractmethod
    def __call__(self, *args: ta.Any, **kwargs: ta.Any) -> T:
        raise NotImplementedError

    def pipe(self, fn: ta.Callable[..., U], *args: ta.Any, **kwargs: ta.Any) -> 'Func[U]':
        return Pipe([self], Bind(fn, *args, **kwargs))

    def __or__(self, fn: ta.Callable[..., U]) -> 'Func[U]':
        return self.pipe(fn)

    def apply(self, fn: ta.Callable[[T], ...], *args: ta.Any, **kwargs: ta.Any) -> 'Func[T]':
        return Pipe([self], Apply(Bind(fn, *args, **kwargs)))

    def __and__(self, fn: ta.Callable[[T], ...]) -> 'Func[T]':
        return self.apply(fn)


class Bind(Func[T]):
    def __init__(self, fn: ta.Callable[..., T], *args: ta.Any, **kwargs: ta.Any) -> None:
        super().__init__()
        if Ellipsis not in args and Ellipsis not in kwargs:
            args += (Ellipsis,)
        self._fn = fn
        self._args = args
        self._kwargs = kwargs

    def __call__(self, *args: ta.Any, **kwargs: ta.Any) -> T:
        fa = []
        for a in self._args:
            if a is Ellipsis:
                fa.extend(args)
            else:
                fa.append(a)

        fkw = {}
        for k, v in self._kwargs.items():
            if v is Ellipsis:
                if len(args) != 1:
                    raise ValueError(args)
                fkw[k] = args[0]
            else:
                fkw[k] = v
        fkw.update(kwargs)

        return self._fn(*fa, **fkw)


class Pipe(Func[T]):
    def __init__(self, lfns: ta.Sequence[ta.Callable], rfn: ta.Callable[..., T]) -> None:
        super().__init__()
        self._lfn, *self._rfns = [*lfns, rfn]

    def __call__(self, *args: ta.Any, **kwargs: ta.Any) -> T:
        o = self._lfn(*args, **kwargs)
        for fn in self._rfns:
            o = fn(o)
        return o


class Apply(Func[T]):
    def __init__(self, *fns: ta.Callable[[T], ...]) -> None:
        super().__init__()
        self._fns = fns

    def __call__(self, o: ta.Any) -> T:  # noqa
        for fn in self._fns:
            fn(o)
        return o


bind = Bind
pipe = Pipe
apply = Apply


##


def _main() -> None:
    assert Bind(operator.add, 1)(2) == 3

    assert Bind(operator.add, 1).\
        pipe(operator.mul, 2)\
        (2) == 6

    assert Bind(operator.add, 1).\
        apply(print).\
        pipe(operator.mul, 2).\
        apply(print)\
        (2) == 6

    assert (Bind(operator.add, 1) & print | Bind(operator.mul, 2) & print)(2) == 6

    assert Bind(operator.truediv, 2)(4) == .5
    assert Bind(operator.truediv, ..., 2)(4) == 2.

    #

    from omlish import check
    from omlish import lang

    def replace_all(f: str, t: str, s: str) -> str:
        return s.replace(f, t)

    fn = bind(strip_suffix, 'Action') | lang.snake_case | bind(replace_all, '_', '-')
    check.equal(fn('FooBarAction'), 'foo-bar')

    fn = bind(strip_suffix, 'Action') | lang.snake_case | bind(str.replace, ..., '_', '-')
    check.equal(fn('FooBarAction'), 'foo-bar')


if __name__ == '__main__':
    _main()
