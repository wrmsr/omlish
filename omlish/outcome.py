# https://github.com/python-trio/outcome/tree/6a3192f306ead4900a33fa8c47e5af5430e37692
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import abc
import dataclasses as dc
import typing as ta

from . import check


ValueT_co = ta.TypeVar('ValueT_co', covariant=True)
ResultT = ta.TypeVar('ResultT')
ArgsT = ta.ParamSpec('ArgsT')


##


class AlreadyUsedError(RuntimeError):
    """An Outcome can only be unwrapped once."""


def _remove_tb_frames(exc: BaseException, n: int) -> BaseException:
    tb: ta.Any = exc.__traceback__
    for _ in range(n):
        check.not_none(tb)
        tb = tb.tb_next
    return exc.with_traceback(tb)


##


@ta.overload
def capture(
        sync_fn: ta.Callable[ArgsT, ta.NoReturn],
        *args: ArgsT.args,
        **kwargs: ArgsT.kwargs,
) -> 'Error':
    ...


@ta.overload
def capture(
        sync_fn: ta.Callable[ArgsT, ResultT],
        *args: ArgsT.args,
        **kwargs: ArgsT.kwargs,
) -> ta.Union['Value[ResultT]', 'Error']:
    ...


def capture(
        sync_fn: ta.Callable[ArgsT, ResultT],
        *args: ArgsT.args,
        **kwargs: ArgsT.kwargs,
) -> ta.Union['Value[ResultT]', 'Error']:
    """
    Run ``sync_fn(*args, **kwargs)`` and capture the result.

    Returns:
      Either a :class:`Value` or :class:`Error` as appropriate.
    """

    try:
        return Value(sync_fn(*args, **kwargs))

    except BaseException as exc:  # noqa
        exc = _remove_tb_frames(exc, 1)
        return Error(exc)


#


@ta.overload
async def acapture(
        async_fn: ta.Callable[ArgsT, ta.Awaitable[ta.NoReturn]],
        *args: ArgsT.args,
        **kwargs: ArgsT.kwargs,
) -> 'Error':
    ...


@ta.overload
async def acapture(
        async_fn: ta.Callable[ArgsT, ta.Awaitable[ResultT]],
        *args: ArgsT.args,
        **kwargs: ArgsT.kwargs,
) -> ta.Union['Value[ResultT]', 'Error']:
    ...


async def acapture(
        async_fn: ta.Callable[ArgsT, ta.Awaitable[ResultT]],
        *args: ArgsT.args,
        **kwargs: ArgsT.kwargs,
) -> ta.Union['Value[ResultT]', 'Error']:
    """
    Run ``await async_fn(*args, **kwargs)`` and capture the result.

    Returns:
      Either a :class:`Value` or :class:`Error` as appropriate.
    """

    try:
        return Value(await async_fn(*args, **kwargs))

    except BaseException as exc:  # noqa
        exc = _remove_tb_frames(exc, 1)
        return Error(exc)


##


@dc.dataclass(repr=False, init=False, slots=True, frozen=True, order=True)
class Outcome(abc.ABC, ta.Generic[ValueT_co]):
    """
    An abstract class representing the result of a Python computation.

    This class has two concrete subclasses: :class:`Value` representing a value, and :class:`Error` representing an
    exception.

    In addition to the methods described below, comparison operators on :class:`Value` and :class:`Error` objects
    (``==``, ``<``, etc.) check that the other object is also a :class:`Value` or :class:`Error` object respectively,
    and then compare the contained objects.

    :class:`Outcome` objects are hashable if the contained objects are hashable.
    """

    _unwrapped: bool = dc.field(default=False, compare=False, init=False)

    def _set_unwrapped(self) -> None:
        if self._unwrapped:
            raise AlreadyUsedError
        object.__setattr__(self, '_unwrapped', True)

    @abc.abstractmethod
    def unwrap(self) -> ValueT_co:
        """
        Return or raise the contained value or exception.

        These two lines of code are equivalent::

           x = fn(*args)
           x = outcome.capture(fn, *args).unwrap()
        """

    @abc.abstractmethod
    def send(self, gen: ta.Generator[ResultT, ValueT_co, object]) -> ResultT:
        """
        Send or throw the contained value or exception into the given generator object.

        Args:
          gen: A generator object supporting ``.send()`` and ``.throw()`` methods.
        """

    @abc.abstractmethod
    async def asend(self, agen: ta.AsyncGenerator[ResultT, ValueT_co]) -> ResultT:
        """
        Send or throw the contained value or exception into the given async generator object.

        Args:
          agen: An async generator object supporting ``.asend()`` and ``.athrow()`` methods.
        """


@ta.final
@dc.dataclass(frozen=True, repr=False, slots=True, order=True)
class Value(Outcome[ValueT_co], ta.Generic[ValueT_co]):
    """Concrete :class:`Outcome` subclass representing a regular value."""

    value: ValueT_co

    def __repr__(self) -> str:
        return f'Value({self.value!r})'

    def unwrap(self) -> ValueT_co:
        self._set_unwrapped()
        return self.value

    def send(self, gen: ta.Generator[ResultT, ValueT_co, object]) -> ResultT:
        self._set_unwrapped()
        return gen.send(self.value)

    async def asend(self, agen: ta.AsyncGenerator[ResultT, ValueT_co]) -> ResultT:
        self._set_unwrapped()
        return await agen.asend(self.value)


@ta.final
@dc.dataclass(frozen=True, repr=False, slots=True, order=True)
class Error(Outcome[ta.NoReturn]):
    """Concrete :class:`Outcome` subclass representing a raised exception."""

    error: BaseException

    def __post_init__(self) -> None:
        if not isinstance(self.error, BaseException):
            raise TypeError(self.error)

    def __repr__(self) -> str:
        return f'Error({self.error!r})'

    def unwrap(self) -> ta.NoReturn:
        self._set_unwrapped()

        # Tracebacks show the 'raise' line below out of context, so let's give this variable a name that makes sense out
        # of context.
        captured_error = self.error

        try:
            raise captured_error

        finally:
            # We want to avoid creating a reference cycle here. Python does collect cycles just fine, so it wouldn't be
            # the end of the world if we did create a cycle, but the cyclic garbage collector adds latency to Python
            # programs, and the more cycles you create, the more often it runs, so it's nicer to avoid creating them in
            # the first place. For more details see:
            #
            #    https://github.com/python-trio/trio/issues/1770
            #
            # In particular, by deleting this local variables from the 'unwrap' methods frame, we avoid the
            # 'captured_error' object's __traceback__ from indirectly referencing 'captured_error'.
            del captured_error, self

    def send(self, gen: ta.Generator[ResultT, ta.NoReturn, object]) -> ResultT:
        self._set_unwrapped()
        return gen.throw(self.error)

    async def asend(self, agen: ta.AsyncGenerator[ResultT, ta.NoReturn]) -> ResultT:
        self._set_unwrapped()
        return await agen.athrow(self.error)


# A convenience alias to a union of both results, allowing exhaustiveness checking.
Maybe = Value[ValueT_co] | Error
