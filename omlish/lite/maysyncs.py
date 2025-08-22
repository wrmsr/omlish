# ruff: noqa: UP006 UP043 UP045
# @omlish-lite
"""
TODO:
 - __del__
"""
import abc
import functools
import inspect
import typing as ta


T = ta.TypeVar('T')
T_co = ta.TypeVar('T_co', covariant=True)

O = ta.TypeVar('O')
O_co = ta.TypeVar('O_co', covariant=True)

I = ta.TypeVar('I')
I_contra = ta.TypeVar('I_contra', contravariant=True)

_MaysyncX = ta.TypeVar('_MaysyncX')

_MaysyncRS = ta.TypeVar('_MaysyncRS')
_MaysyncRA = ta.TypeVar('_MaysyncRA')


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


class _MaywaitableLike(
    abc.ABC,
    ta.Generic[_MaysyncX],
):
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


class _Maywaitable(
    _MaywaitableLike[_MaysyncX],
    abc.ABC,
    ta.Generic[_MaysyncX, T],
):
    def m(self) -> ta.Awaitable[T]:
        return _MaysyncFuture(_MaysyncOp(
            self._x,
            self._args,
            self._kwargs,
        ))


class _MaysyncGenerator(
    _MaywaitableLike[_MaysyncX],
    abc.ABC,
    ta.Generic[_MaysyncX, O, I],
):
    def m(self) -> ta.AsyncGenerator[O, I]:
        return _MaysyncGeneratorFuture(_MaysyncOp(  # noqa
            self._x,
            self._args,
            self._kwargs,
        ))


##


class _FpMaysyncFnLike(
    abc.ABC,
    ta.Generic[_MaysyncRS, _MaysyncRA],
):
    def __init__(
            self,
            s: ta.Callable[..., _MaysyncRS],
            a: ta.Callable[..., _MaysyncRA],
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
        return self.__class__(
            self._s.__get__(instance, owner),  # noqa
            self._a.__get__(instance, owner),  # noqa
        )


@ta.final
class _FpMaysyncFn(
    _FpMaysyncFnLike[T, ta.Awaitable[T]],
    MaysyncFn_[T],
    ta.Generic[T],
):
    def __call__(self, *args, **kwargs):
        return _FpMaywaitable(self, args, kwargs)


@ta.final
class _FpMaywaitable(
    _Maywaitable[_FpMaysyncFn[T], T],
):
    def s(self) -> T:
        return self._x._s(*self._args, **self._kwargs)  # noqa

    async def a(self) -> T:
        return await self._x._a(*self._args, **self._kwargs)  # noqa


def make_maysync_fn(
        s: ta.Callable[..., T],
        a: ta.Callable[..., ta.Awaitable[T]],
) -> MaysyncFn[T]:
    return _FpMaysyncFn(s, a)


@ta.final
class _FpMaysyncGeneratorFn(
    _FpMaysyncFnLike[ta.Generator[O, I, None], ta.AsyncGenerator[O, I]],
    MaysyncGeneratorFn_[O, I],
    ta.Generic[O, I],
):
    def __call__(self, *args, **kwargs):
        return _FpMaysyncGenerator(self, args, kwargs)


@ta.final
class _FpMaysyncGenerator(
    _MaysyncGenerator[_FpMaysyncGeneratorFn[O, I], O, I],
):
    def s(self) -> ta.Generator[O, I, None]:
        # FIXME: I???
        yield from self._x._s(*self._args, **self._kwargs)  # noqa

    async def a(self) -> ta.AsyncGenerator[O, I]:
        # FIXME: I???
        async for o in self._x._a(*self._args, **self._kwargs):  # noqa
            yield o


def make_maysync_generator_fn(
        s: ta.Callable[..., ta.Generator[O, I, None]],
        a: ta.Callable[..., ta.AsyncGenerator[O, I]],
) -> MaysyncGeneratorFn[O, I]:
    return _FpMaysyncGeneratorFn(s, a)


@ta.overload
def make_maysync(
        s: ta.Callable[..., T],
        a: ta.Callable[..., ta.Awaitable[T]],
) -> MaysyncFn[T]:
    ...


@ta.overload
def make_maysync(
        s: ta.Callable[..., ta.Generator[O, I, None]],
        a: ta.Callable[..., ta.AsyncGenerator[O, I]],
) -> MaysyncGeneratorFn[O, I]:
    ...


def make_maysync(s, a):
    # FIXME: lame and fat import
    if inspect.isasyncgenfunction(a):
        return make_maysync_generator_fn(s, a)
    else:
        return make_maysync_fn(s, a)


##


class _MgMaysyncFnLike(
    abc.ABC,
    ta.Generic[T],
):
    def __init__(
            self,
            mg: ta.Callable[..., T],
    ) -> None:
        self._mg = mg

        functools.update_wrapper(self, mg, updated=())

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}({self._mg!r})'

    def fn_pair(self) -> ta.Optional[Maysync_.FnPair]:
        return None

    def __get__(self, instance, owner=None):
        return self.__class__(
            self._mg.__get__(instance, owner),  # noqa
        )

    @abc.abstractmethod  # noqa
    def __call__(self, *args, **kwargs):
        raise NotImplementedError


class _MgMaysyncFn(
    _MgMaysyncFnLike[ta.Generator['_MaysyncOp', ta.Any, T]],
    MaysyncFn_[T],
    ta.Generic[T],
):
    def __call__(self, *args, **kwargs):
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


class _MgMaysyncGeneratorFn(
    _MgMaysyncFnLike[ta.Any],  # ?? #ta.Generator['_MaysyncOp', ta.Any, T]],
    MaysyncGeneratorFn_[O, I],
    ta.Generic[O, I],
):
    def __call__(self, *args, **kwargs):
        return _MgMaysyncGenerator(self, args, kwargs)


@ta.final
class _MgMaysyncGenerator(
    _MaysyncGenerator[_MgMaysyncGeneratorFn[O, I], O, I],
):
    def s(self) -> ta.Generator[O, I, None]:
        # FIXME: I???
        # yield from self._x._s(*self._args, **self._kwargs)  # noqa
        raise NotImplementedError
        yield  # type: ignore[unreachable]  # noqa

    async def a(self) -> ta.AsyncGenerator[O, I]:
        # # FIXME: I???
        # async for o in self._x._a(*self._args, **self._kwargs):  # noqa
        #     yield o
        raise NotImplementedError
        yield  # type: ignore[unreachable]  # noqa


#


class _MgDriverLike(abc.ABC):
    def __init__(self, m):
        self._m = m

        functools.update_wrapper(self, m, updated=())

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}({self._m!r})'

    def __get__(self, instance, owner=None):
        return self.__class__(
            self._m.__get__(instance, owner),
        )

    @abc.abstractmethod
    def __call__(self, *args, **kwargs):
        raise NotImplementedError


@ta.final
class _MgDriver(_MgDriverLike):
    def __call__(self, *args, **kwargs):
        a_ = self._m(*args, **kwargs)
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


def maysync_fn(
        m: ta.Callable[..., ta.Awaitable[T]],
) -> MaysyncFn[T]:
    return _MgMaysyncFn(_MgDriver(m))


@ta.final
class _MgGeneratorDriver(_MgDriverLike):
    def __call__(self, *args, **kwargs):
        a_ = self._m(*args, **kwargs)
        try:
            a = a_.__await__()
            a_.__aiter__()  # ???
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


def maysync_generator_fn(
        m: ta.Callable[..., ta.AsyncGenerator[O, I]],
) -> MaysyncGeneratorFn[O, I]:
    return _MgMaysyncGeneratorFn(_MgGeneratorDriver(m))


@ta.overload
def maysync(m: ta.Callable[..., ta.Awaitable[T]]) -> MaysyncFn[T]:
    ...


@ta.overload
def maysync(m: ta.Callable[..., ta.AsyncGenerator[O, I]]) -> MaysyncGeneratorFn[O, I]:
    ...


def maysync(m):
    if inspect.isasyncgenfunction(m):
        return maysync_generator_fn(m)
    else:
        return maysync_fn(m)


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


@ta.final
class _MaysyncGeneratorFuture(ta.Generic[O, I]):
    def __init__(
            self,
            op: _MaysyncOp,
    ) -> None:
        self.op = op

    def __aiter__(self):
        return self

    async def __anext__(self):
        return await self.asend(None)

    async def asend(self, value):
        # raise StopAsyncIteration
        raise NotImplementedError

    async def athrow(self, typ, val=None, tb=None):
        # if val is None:
        #     if tb is None:
        #         raise typ
        #     val = typ()
        # if tb is not None:
        #     val = val.with_traceback(tb)
        # raise val
        raise NotImplementedError

    async def aclose(self):
        # try:
        #     await self.athrow(GeneratorExit)
        # except (GeneratorExit, StopAsyncIteration):
        #     pass
        # else:
        #     raise RuntimeError("asynchronous generator ignored GeneratorExit")
        raise NotImplementedError
