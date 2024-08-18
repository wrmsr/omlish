# -*- coding: utf-8 -*-


# You can diff these tests with those for ``ExitStack`` in the hope of showing
# how good our asynchronous counterpart is.


import pytest

from aiotk import AsyncExitStack
from unittest import mock


class AutoClose(object):
    """Example synchronous context manager."""

    def __init__(self, h, v=None, suppress=False):
        self._h = h
        self._v = v
        self._suppress = suppress

    async def __aenter__(self):
        return self._v

    async def __aexit__(self, etype, val, tb):
        self._h.close(etype, val, tb)
        return self._suppress


@pytest.mark.asyncio
async def test_exit_stack_noop():
    async with AsyncExitStack():
        pass


@pytest.mark.asyncio
async def test_exit_stack():

    handle = mock.MagicMock()
    async with AsyncExitStack() as stack:
        await stack.enter_context(AutoClose(handle))
    handle.close.assert_called_once_with(None, None, None)


@pytest.mark.asyncio
async def test_exit_stack_exception_propagate():

    h1 = mock.MagicMock()
    h2 = mock.MagicMock()
    v1 = mock.MagicMock()
    v2 = mock.MagicMock()
    error = ValueError('FUUU')

    with pytest.raises(ValueError) as exc:
        async with AsyncExitStack() as stack:
            v = await stack.enter_context(AutoClose(h1, v=v1))
            assert v is v1
            v = await stack.enter_context(AutoClose(h2, v=v2))
            assert v is v2
            raise error
    assert exc.value is error

    h2.close.assert_called_once_with(ValueError, error, mock.ANY)
    h1.close.assert_called_once_with(ValueError, error, mock.ANY)


@pytest.mark.asyncio
async def test_exit_stack_exception_suppress():

    h1 = mock.MagicMock()
    h2 = mock.MagicMock()
    error = ValueError('FUUU')

    async with AsyncExitStack() as stack:
        await stack.enter_context(AutoClose(h1))
        await stack.enter_context(AutoClose(h2, suppress=True))
        raise error

    h2.close.assert_called_once_with(ValueError, error, mock.ANY)
    h1.close.assert_called_once_with(None, None, None)


@pytest.mark.asyncio
async def test_exit_stack_exception_substitution():

    h1 = mock.MagicMock()
    h2 = mock.MagicMock()
    e1 = ValueError('FUUU')
    e2 = KeyError('oops')

    class FailingAutoClose(object):
        """."""

        def __init__(self, h):
            self._h = h

        def __enter__(self):
            return self

        def __exit__(self, etype, val, tb):
            assert etype is ValueError
            assert val is e1
            assert tb
            self._h.close(etype, val, tb)
            raise e2

    with pytest.raises(KeyError) as exc:
        async with AsyncExitStack() as stack:
            await stack.enter_context(AutoClose(h1))
            await stack.enter_context(FailingAutoClose(h2))
            raise e1
    assert exc.value is e2

    h2.close.assert_called_once_with(ValueError, e1, mock.ANY)
    h1.close.assert_called_once_with(KeyError, e2, mock.ANY)
