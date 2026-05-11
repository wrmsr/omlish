# PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2
# --------------------------------------------
#
# 1. This LICENSE AGREEMENT is between the Python Software Foundation ("PSF"), and the Individual or Organization
# ("Licensee") accessing and otherwise using this software ("Python") in source or binary form and its associated
# documentation.
#
# 2. Subject to the terms and conditions of this License Agreement, PSF hereby grants Licensee a nonexclusive,
# royalty-free, world-wide license to reproduce, analyze, test, perform and/or display publicly, prepare derivative
# works, distribute, and otherwise use Python alone or in any derivative version, provided, however, that PSF's License
# Agreement and PSF's notice of copyright, i.e., "Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009,
# 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017 Python Software Foundation; All Rights Reserved" are retained in Python
# alone or in any derivative version prepared by Licensee.
#
# 3. In the event Licensee prepares a derivative work that is based on or incorporates Python or any part thereof, and
# wants to make the derivative work available to others as provided herein, then Licensee hereby agrees to include in
# any such work a brief summary of the changes made to Python.
#
# 4. PSF is making Python available to Licensee on an "AS IS" basis.  PSF MAKES NO REPRESENTATIONS OR WARRANTIES,
# EXPRESS OR IMPLIED.  BY WAY OF EXAMPLE, BUT NOT LIMITATION, PSF MAKES NO AND DISCLAIMS ANY REPRESENTATION OR WARRANTY
# OF MERCHANTABILITY OR FITNESS FOR ANY PARTICULAR PURPOSE OR THAT THE USE OF PYTHON WILL NOT INFRINGE ANY THIRD PARTY
# RIGHTS.
#
# 5. PSF SHALL NOT BE LIABLE TO LICENSEE OR ANY OTHER USERS OF PYTHON FOR ANY INCIDENTAL, SPECIAL, OR CONSEQUENTIAL
# DAMAGES OR LOSS AS A RESULT OF MODIFYING, DISTRIBUTING, OR OTHERWISE USING PYTHON, OR ANY DERIVATIVE THEREOF, EVEN IF
# ADVISED OF THE POSSIBILITY THEREOF.
#
# 6. This License Agreement will automatically terminate upon a material breach of its terms and conditions.
#
# 7. Nothing in this License Agreement shall be deemed to create any relationship of agency, partnership, or joint
# venture between PSF and Licensee.  This License Agreement does not grant permission to use PSF trademarks or trade
# name in a trademark sense to endorse or promote products or services of Licensee, or any third party.
#
# 8. By copying, installing or otherwise using Python, Licensee agrees to be bound by the terms and conditions of this
# License Agreement.
import contextlib
import sys
import threading
import types
import typing as ta

from .. import check
from .. import collections as col
from .. import lang


T = ta.TypeVar('T')


##


class BaseKeyedExitStack:
    """A base class for KeyedExitStack and AsyncKeyedExitStack."""

    def __init__(self) -> None:
        super().__init__()

        self.__lock = threading.Lock()
        self.__cb_lst: col.OpenLinkedList[BaseKeyedExitStack._Callback] = col.OpenLinkedList()
        self.__cb_dct: dict[ta.Any, col.OpenLinkedList.Node[BaseKeyedExitStack._Callback]] = {}

    #

    class _Callback(ta.NamedTuple):
        fn: ta.Callable
        is_async: bool
        key: ta.Any

    def _push_callback(
            self,
            callback: ta.Callable,
            *,
            is_async: bool = False,
            key: ta.Any | None = None,
    ) -> None:
        cb = self._Callback(
            callback,
            is_async,
            key,
        )

        with self.__lock:
            if key is not None:
                check.not_in(key, self.__cb_dct)

            node = self.__cb_lst.new_node(cb)

            if key is not None:
                self.__cb_dct[key] = node

            self.__cb_lst.append_node(node)

    def _pop_callback(self) -> _Callback | None:
        with self.__lock:
            if (node := self.__cb_lst.tail_node) is None:
                return None

            cb = node.value

            self.__cb_lst.unlink_node(node)

            if cb.key is not None:
                del self.__cb_dct[cb.key]

            return cb

    def _unlink_keyed_callback(
            self,
            key: ta.Any,
            *,
            can_be_async: bool,
    ) -> _Callback:
        check.not_none(key)

        with self.__lock:
            node = self.__cb_dct[key]

            cb = node.value

            if not can_be_async:
                check.state(not cb.is_async)

            self.__cb_lst.unlink_node(node)

            return cb

    #

    def enter_context(
            self,
            cm: ta.ContextManager[T],
            *,
            key: ta.Any | None = None,
    ) -> T:
        # We look up the special methods on the type to match the with statement.
        cls = type(cm)
        try:
            _enter = cls.__enter__
            _exit = cls.__exit__
        except AttributeError:
            raise TypeError(
                f"'{cls.__module__}.{cls.__qualname__}' object does not support the context manager protocol",
            ) from None

        result = _enter(cm)

        self._push_callback(
            types.MethodType(_exit, cm),
            key=key,
        )

        return result

    #

    @staticmethod
    def _fix_exception_context(new_exc, old_exc, frame_exc):
        # Context may not be correct, so find the end of the chain
        while True:
            exc_context = new_exc.__context__
            if exc_context is None or exc_context is old_exc:
                # Context is already set correctly (see issue 20317)
                return
            if exc_context is frame_exc:
                break
            new_exc = exc_context
        # Change the end of the chain to point to the exception we expect it to reference
        new_exc.__context__ = old_exc

    @staticmethod
    def _raise_pending_exception(exc: BaseException) -> ta.NoReturn:
        try:
            # bare "raise exc" replaces our carefully set-up context
            fixed_ctx = exc.__context__
            raise exc
        except BaseException:
            exc.__context__ = fixed_ctx  # noqa
            raise

    #

    def exit_keyed_context(
            self,
            key: ta.Any,
            exc_info: lang.ExcInfo | None = None,
    ) -> bool | None:
        cb = self._unlink_keyed_callback(key, can_be_async=False)

        args = lang.opt_exc_info(exc_info)

        return cb.fn(*args)


##


class KeyedExitStack(BaseKeyedExitStack, contextlib.AbstractContextManager):
    def __enter__(self) -> ta.Self:
        return self

    def close(self) -> None:
        self.__exit__(None, None, None)

    def __exit__(
            self,
            exc_ty: type[BaseException] | None = None,
            exc: BaseException | None = None,
            exc_tb: types.TracebackType | None = None,
    ) -> bool | None:
        received_exc = exc is not None

        # We manipulate the exception state so it behaves as though we were actually nesting multiple with statements
        frame_exc = sys.exception()

        # Callbacks are invoked in LIFO order to match the behavior of nested context managers
        suppressed_exc = False
        pending_raise = False
        while (cb := self._pop_callback()) is not None:
            check.state(not cb.is_async)

            try:
                if exc is None:
                    exc_details: lang.OptExcInfo = None, None, None
                else:
                    exc_details = type(exc), exc, exc.__traceback__

                cb_suppress = cb.fn(*exc_details)

                if cb_suppress:
                    suppressed_exc = True
                    pending_raise = False
                    exc = None

            except BaseException as new_exc:  # noqa
                # simulate the stack of exceptions by setting the context
                self._fix_exception_context(new_exc, exc, frame_exc)
                pending_raise = True
                exc = new_exc

        if pending_raise:
            self._raise_pending_exception(exc)  # type: ignore[arg-type]

        return received_exc and suppressed_exc


##


class AsyncKeyedExitStack(BaseKeyedExitStack, contextlib.AbstractAsyncContextManager):
    async def enter_async_context(
            self,
            cm: ta.AsyncContextManager[T],
            *,
            key: ta.Any | None = None,
    ) -> T:
        # We look up the special methods on the type to match the with statement.
        cls = type(cm)
        try:
            _enter = cls.__aenter__
            _exit = cls.__aexit__
        except AttributeError:
            raise TypeError(
                f"'{cls.__module__}.{cls.__qualname__}' object does not support the asynchronous context manager "
                f"protocol",
            ) from None

        result = await _enter(cm)

        self._push_callback(
            types.MethodType(_exit, cm),
            is_async=True,
            key=key,
        )

        return result

    #

    async def __aenter__(self) -> ta.Self:
        return self

    async def aclose(self) -> None:
        await self.__aexit__(None, None, None)

    async def __aexit__(
            self,
            exc_ty: type[BaseException] | None = None,
            exc: BaseException | None = None,
            exc_tb: types.TracebackType | None = None,
    ) -> bool | None:
        received_exc = exc is not None

        # We manipulate the exception state so it behaves as though we were actually nesting multiple with statements
        frame_exc = sys.exception()

        # Callbacks are invoked in LIFO order to match the behavior of nested context managers
        suppressed_exc = False
        pending_raise = False
        while (cb := self._pop_callback()) is not None:
            try:
                if exc is None:
                    exc_details: lang.OptExcInfo = None, None, None
                else:
                    exc_details = type(exc), exc, exc.__traceback__

                if cb.is_async:
                    cb_suppress = await cb.fn(*exc_details)
                else:
                    cb_suppress = cb.fn(*exc_details)

                if cb_suppress:
                    suppressed_exc = True
                    pending_raise = False
                    exc = None

            except BaseException as new_exc:  # noqa
                # simulate the stack of exceptions by setting the context
                self._fix_exception_context(new_exc, exc, frame_exc)
                pending_raise = True
                exc = new_exc

        if pending_raise:
            self._raise_pending_exception(exc)  # type: ignore[arg-type]

        return received_exc and suppressed_exc

    #

    async def async_exit_keyed_context(
            self,
            key: ta.Any,
            exc_info: lang.ExcInfo | None = None,
    ) -> bool | None:
        cb = self._unlink_keyed_callback(key, can_be_async=True)

        args = lang.opt_exc_info(exc_info)

        if cb.is_async:
            return await cb.fn(*args)
        else:
            return cb.fn(*args)
