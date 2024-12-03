import abc
import typing as ta

from .maybes import Maybe


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


##


@ta.runtime_checkable
class GeneratorLike(ta.Protocol[O_co, I_contra, R_co]):
    def send(self, i: I_contra) -> O_co:  # Raises[StopIteration[R_co]]
        ...

    def close(self) -> None:
        ...


class GeneratorLike_(abc.ABC, ta.Generic[O, I, R]):  # noqa
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


class Generator(ta.Generator[O, I, R]):
    def __init__(self, g: ta.Generator[O, I, R]) -> None:
        super().__init__()
        self._g = g

    @property
    def g(self) -> ta.Generator[O, I, R]:
        return self._g

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

    def close(self):
        self._g.close()


##


class CoroutineGenerator(ta.Generic[O, I, R]):
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

    #

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


corogen = CoroutineGenerator
