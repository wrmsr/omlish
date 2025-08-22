# ruff: noqa: UP006 UP043 UP045
# @omlish-lite
"""
TODO:
 - __del__
"""
import abc
import functools
import types
import typing as ta


T = ta.TypeVar('T')
T_co = ta.TypeVar('T_co', covariant=True)

O = ta.TypeVar('O')
O_co = ta.TypeVar('O_co', covariant=True)

I = ta.TypeVar('I')
I_contra = ta.TypeVar('I_contra', contravariant=True)

_MaysyncX = ta.TypeVar('_MaysyncX')


##


class Maywaitable(ta.Protocol[T_co]):
    def s(self) -> T_co:
        ...

    def a(self) -> ta.Awaitable[T_co]:
        ...

    def m(self) -> ta.Awaitable[T_co]:
        ...


class MaysyncGenerator(ta.Protocol[O_co, I_contra]):
    def s(self) -> ta.Generator[O_co, I_contra, None]:
        ...

    def a(self) -> ta.AsyncGenerator[O_co, I_contra]:
        ...

    def m(self) -> ta.AsyncGenerator[O_co, I_contra]:
        ...


MaysyncFn = ta.Callable[..., Maywaitable[T]]  # ta.TypeAlias  # omlish-amalg-typing-no-move
MaysyncGeneratorFn = ta.Callable[..., MaysyncGenerator[O, I]]  # ta.TypeAlias  # omlish-amalg-typing-no-move


class Maysync_(abc.ABC):  # noqa
    def __init_subclass__(cls, **kwargs):
        if Maysync_ in cls.__bases__ and abc.ABC not in cls.__bases__:
            raise TypeError(cls)

        super().__init_subclass__(**kwargs)

    class FnPair(ta.NamedTuple):
        s: ta.Callable[..., ta.Any]
        a: ta.Callable[..., ta.Any]

    @abc.abstractmethod
    def fn_pair(self) -> ta.Optional[FnPair]:
        raise NotImplementedError

    @abc.abstractmethod
    def cast(self):
        pass

    @abc.abstractmethod
    def __call__(self, *args, **kwargs):  # -> Maywaitable[T]
        raise NotImplementedError


class MaysyncFn_(Maysync_, abc.ABC, ta.Generic[T]):  # noqa
    @ta.final
    def cast(self) -> MaysyncFn[T]:
        return ta.cast('MaysyncFn[T]', self)


class MaysyncGeneratorFn_(Maysync_, abc.ABC, ta.Generic[O, I]):  # noqa
    @ta.final
    def cast(self) -> MaysyncGenerator[O, I]:
        return ta.cast('MaysyncGenerator[O, I]', self)


##


class _MaywaitableLike(abc.ABC, ta.Generic[_MaysyncX]):
    @ta.final
    def __init__(
            self,
            x: _MaysyncX,
            args: ta.Tuple[ta.Any, ...],
            kwargs: ta.Mapping[str, ta.Any],
    ) -> None:
        self._x = x
        self._args = args
        self._kwargs = kwargs

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}({self._x!r})'


class _Maywaitable(_MaywaitableLike[_MaysyncX], abc.ABC, ta.Generic[_MaysyncX, T]):
    def m(self) -> ta.Awaitable[T]:
        return _MaysyncFuture(_MaysyncOp(
            self._x,
            self._args,
            self._kwargs,
        ))


# class _MaysyncGenerator(_MaywaitableLike[_MaysyncX], abc.ABC, ta.Generic[_MaysyncX, O, I]):
#     def m(self) -> ta.AsyncGenerator[O, I]:
#         return _MaysyncFuture(_MaysyncOp(
#             self._x,
#             self._args,
#             self._kwargs,
#         ))


##


@ta.final
class _FnMaysyncFn(MaysyncFn_[T], ta.Generic[T]):
    def __init__(
            self,
            s: ta.Callable[..., T],
            a: ta.Callable[..., ta.Awaitable[T]],
    ) -> None:
        if s is None:
            raise TypeError(s)
        if a is None:
            raise TypeError(a)
        self._s = s
        self._a = a

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}({self._s!r}, {self._a!r})'

    def fn_pair(self) -> ta.Optional[Maysync_.FnPair]:
        return Maysync_.FnPair(
            self._s,
            self._a,
        )

    def __get__(self, instance, owner=None):
        return _FnMaysyncFn(
            self._s.__get__(instance, owner),  # noqa
            self._a.__get__(instance, owner),  # noqa
        )

    def __call__(self, *args, **kwargs):
        return _FnMaywaitable(self, args, kwargs)


@ta.final
class _FnMaywaitable(_Maywaitable[_FnMaysyncFn[T], T]):
    def s(self) -> T:
        return self._x._s(*self._args, **self._kwargs)  # noqa

    async def a(self) -> T:
        return await self._x._a(*self._args, **self._kwargs)  # noqa


def make_maysync(
        s: ta.Callable[..., T],
        a: ta.Callable[..., ta.Awaitable[T]],
) -> MaysyncFn[T]:
    return _FnMaysyncFn(s, a)


##


@ta.final
class _MgMaysyncFn(MaysyncFn_[T], ta.Generic[T]):
    def __init__(
            self,
            mg: ta.Callable[..., ta.Generator['_MaysyncOp', ta.Any, T]],
    ) -> None:
        self._mg = mg

        functools.update_wrapper(self, mg, updated=())

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}({self._mg!r})'

    def fn_pair(self) -> ta.Optional[Maysync_.FnPair]:
        return None

    def __get__(self, instance, owner=None):
        return _MgMaysyncFn(
            self._mg.__get__(instance, owner),  # noqa
        )

    # _is_ag_: ta.Optional[bool] = None
    #
    # def _is_ag(self) -> bool:
    #     if self._is_ag_ is None:
    #         if isinstance(self._mg, _MgWrapper):
    #             self._is_ag_ = self._mg._is_ag  # noqa
    #         else:
    #             self._is_ag_ = inspect.isasyncgenfunction(self._mg)
    #     return self._is_ag_

    def __call__(self, *args, **kwargs):
        # if self._is_ag():
        #     raise NotImplementedError
        # else:
        return _MgMaywaitable(self, args, kwargs)


@ta.final
class _MgMaywaitable(_Maywaitable[_MgMaysyncFn[T], T]):
    def s(self) -> T:
        g = self._x._mg(*self._args, **self._kwargs)  # noqa

        i: ta.Any = None
        e: ta.Any = None

        while True:
            try:
                if e is not None:
                    o = g.throw(e)
                else:
                    o = g.send(i)
            except StopIteration as ex:
                return ex.value

            i = None
            e = None

            if not isinstance(o, _MaysyncOp):
                raise TypeError(o)

            try:
                i = o.x(*o.args, **o.kwargs).s()
            except BaseException as ex:  # noqa
                e = ex

            del o

    async def a(self) -> T:
        g = self._x._mg(*self._args, **self._kwargs)  # noqa

        i: ta.Any = None
        e: ta.Any = None

        while True:
            try:
                if e is not None:
                    o = g.throw(e)
                else:
                    o = g.send(i)
            except StopIteration as ex:
                return ex.value

            i = None
            e = None

            if not isinstance(o, _MaysyncOp):
                raise TypeError(o)

            try:
                i = await o.x(*o.args, **o.kwargs).a()
            except BaseException as ex:  # noqa
                e = ex

            del o


@ta.final
class _MgWrapper:
    def __init__(
            self,
            m,
            # *,
            # is_ag=None,
    ):
        self._m = m

        # if is_ag is None:
        #     is_ag = inspect.isasyncgenfunction(m)
        # self._is_ag = is_ag

        functools.update_wrapper(self, m, updated=())

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}@{id(self):x}({self._m!r}' +  # noqa
            # (f', is_ag={self._is_ag!r}' if self._is_ag else '') +
            f')'
        )

    def __get__(self, instance, owner=None):
        return _MgWrapper(
            self._m.__get__(instance, owner),
            # is_ag=self._is_ag,
        )

    def __call__(self, *args, **kwargs):
        a_ = self._m(*args, **kwargs)

        if isinstance(a_, types.AsyncGeneratorType):
            raise NotImplementedError

        else:
            try:
                a = a_.__await__()
                try:
                    g = iter(a)
                    try:
                        while True:
                            try:
                                o = g.send(None)
                            except StopIteration as e:
                                return e.value

                            if not isinstance(o, _MaysyncFuture):
                                raise TypeError(o)

                            if not o.done:
                                try:
                                    o.result = yield o.op
                                except BaseException as e:  # noqa
                                    o.error = e
                                o.done = True

                            del o

                    finally:
                        g.close()

                finally:
                    a.close()

            finally:
                a_.close()


def maysync(m: ta.Callable[..., ta.Awaitable[T]]) -> MaysyncFn[T]:
    return _MgMaysyncFn(_MgWrapper(m))


##


@ta.final
class _MaysyncOp:
    def __init__(
            self,
            x: ta.Any,
            args: ta.Tuple[ta.Any, ...],
            kwargs: ta.Mapping[str, ta.Any],
    ) -> None:
        self.x = x
        self.args = args
        self.kwargs = kwargs

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}({self.x!r})'


class _MaysyncFutureNotAwaitedError(RuntimeError):
    pass


@ta.final
class _MaysyncFuture(ta.Generic[T]):
    def __init__(
            self,
            op: _MaysyncOp,
    ) -> None:
        self.op = op

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}({self.op!r}, done={self.done!r})'

    done: bool = False
    result: T
    error: ta.Optional[BaseException] = None

    def __await__(self):
        if not self.done:
            yield self
        if not self.done:
            raise _MaysyncFutureNotAwaitedError
        if self.error is not None:
            raise self.error
        else:
            return self.result
