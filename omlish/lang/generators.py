import abc
import functools
import typing as ta

from ..lite.abstract import Abstract
from ..lite.maybes import Maybe


T = ta.TypeVar('T')
I = ta.TypeVar('I')
O = ta.TypeVar('O')
R = ta.TypeVar('R')
I_contra = ta.TypeVar('I_contra', contravariant=True)
O_co = ta.TypeVar('O_co', covariant=True)
R_co = ta.TypeVar('R_co', covariant=True)


##


def nextgen(g: T) -> T:
    next(g)  # type: ignore
    return g


def autostart(fn):
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        g = fn(*args, **kwargs)
        if (o := next(g)) is not None:
            raise TypeError(o)
        return g
    return inner


##


@ta.runtime_checkable
class GeneratorLike(ta.Protocol[O_co, I_contra, R_co]):
    def send(self, i: I_contra) -> O_co:  # Raises[StopIteration[R_co]]
        ...

    def close(self) -> None:
        ...


class GeneratorLike_(Abstract, ta.Generic[O, I, R]):  # noqa
    @abc.abstractmethod
    def send(self, i: I) -> O:  # Raises[StopIteration[R]]
        raise NotImplementedError

    def close(self) -> None:
        pass


@ta.overload
def adapt_generator_like(gl: GeneratorLike_[O, I, R]) -> ta.Generator[O, I, R]:
    ...


@ta.overload
def adapt_generator_like(gl: GeneratorLike[O, I, R]) -> ta.Generator[O, I, R]:
    ...


def adapt_generator_like(gl):
    try:
        i = yield
        while True:
            i = yield gl.send(i)
    except StopIteration as e:
        return e.value
    finally:
        gl.close()


##


class AbstractGeneratorCapture(Abstract, ta.Generic[O, I, R]):
    def __init__(self, g: ta.Generator[O, I, R]) -> None:
        super().__init__()

        self._g = g

    @property
    def g(self) -> ta.Generator[O, I, R]:
        return self._g

    #

    def close(self) -> None:
        self._g.close()

    def __enter__(self) -> ta.Self:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._g.close()


class GeneratorCapture(AbstractGeneratorCapture[O, I, R], ta.Generator[O, I, R]):
    value: R

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return next(self._g)
        except StopIteration as e:
            self.value = e.value
            raise

    def send(self, v):
        try:
            return self._g.send(v)
        except StopIteration as e:
            self.value = e.value
            raise

    def throw(self, *args):
        try:
            return self._g.throw(*args)
        except StopIteration as e:
            self.value = e.value
            raise


capture_generator = GeneratorCapture


class CoroutineGeneratorCapture(AbstractGeneratorCapture[O, I, R]):
    class Output(ta.NamedTuple, ta.Generic[T]):
        v: T

        @property
        def is_return(self) -> bool:
            raise NotImplementedError

    class Yield(Output[T]):
        @property
        def is_return(self) -> bool:
            return False

    class Return(Output[T]):
        @property
        def is_return(self) -> bool:
            return True

    class Nothing:
        def __new__(cls):
            raise TypeError

    #

    def send(self, /, v: I | type[Nothing] = Nothing) -> Yield[O] | Return[R]:
        try:
            if v is self.Nothing:
                o = next(self._g)
            else:
                o = self._g.send(v)  # type: ignore[arg-type]
        except StopIteration as e:
            return self.Return(e.value)
        else:
            return self.Yield(o)

    def send_opt(self, v: I | None) -> Yield[O] | Return[R]:
        return self.send(v if v is not None else self.Nothing)

    def send_maybe(self, v: Maybe[I]) -> Yield[O] | Return[R]:
        return self.send(v.or_else(self.Nothing))

    def throw(self, v: BaseException) -> Yield[O] | Return[R]:
        try:
            o = self._g.throw(v)
        except StopIteration as e:
            return self.Return(e.value)
        else:
            return self.Yield(o)


capture_coroutine = CoroutineGeneratorCapture


##


class GeneratorMappedIterator(ta.Generic[O, I, R]):
    """
    Like a `map` iterator but takes a generator instead of a function. Provided generator *must* yield outputs 1:1 with
    inputs.

    Generator return value will be captured on `value` property - present if the generator stopped, absent if the
    iterator stopped.
    """

    def __init__(self, g: ta.Generator[O, I, R], it: ta.Iterator[I]) -> None:
        super().__init__()

        self._g = g
        self._it = it
        self._value: Maybe[R] = Maybe.empty()

    @property
    def g(self) -> ta.Generator[O, I, R]:
        return self._g

    @property
    def it(self) -> ta.Iterator[I]:
        return self._it

    @property
    def value(self) -> Maybe[R]:
        return self._value

    def __iter__(self) -> ta.Iterator[O]:
        return self

    def __next__(self) -> O:
        i = next(self._it)
        try:
            o = self._g.send(i)
        except StopIteration as e:
            self._value = Maybe.just(e.value)
            raise StopIteration from e
        return o


def genmap(g: ta.Generator[O, I, R], it: ta.Iterable[I]) -> GeneratorMappedIterator[O, I, R]:
    return GeneratorMappedIterator(g, iter(it))
