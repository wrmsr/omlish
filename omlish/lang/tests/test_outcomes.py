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
import asyncio
import sys
import traceback

import pytest

from .. import outcomes


##


def test_outcome():
    v = outcomes.Value(1)
    assert v.value() == 1
    assert v.unwrap() == 1
    assert repr(v) == 'Value(1)'

    with pytest.raises(outcomes.OutcomeAlreadyUnwrappedError):
        v.unwrap()

    v = outcomes.Value(1)

    exc = RuntimeError('oops')
    e = outcomes.Error(exc)
    assert e.error() is exc
    with pytest.raises(RuntimeError):
        e.unwrap()
    with pytest.raises(outcomes.OutcomeAlreadyUnwrappedError):
        e.unwrap()
    assert repr(e) == f'Error({exc!r})'

    e = outcomes.Error(exc)
    with pytest.raises(TypeError):
        outcomes.Error('hello')  # type: ignore
    with pytest.raises(TypeError):
        outcomes.Error(RuntimeError)  # type: ignore

    def expect_1():
        assert (yield) == 1
        yield 'ok'

    it = iter(expect_1())
    next(it)
    assert v.send(it) == 'ok'
    with pytest.raises(outcomes.OutcomeAlreadyUnwrappedError):
        v.send(it)

    def expect_runtime_error():
        with pytest.raises(RuntimeError):
            yield
        yield 'ok'

    it = iter(expect_runtime_error())
    next(it)
    assert e.send(it) == 'ok'
    with pytest.raises(outcomes.OutcomeAlreadyUnwrappedError):
        e.send(it)


def test_outcome_eq_hash():
    v1 = outcomes.Value(['hello'])
    v2 = outcomes.Value(['hello'])
    v3 = outcomes.Value('hello')
    v4 = outcomes.Value('hello')
    assert v1 == v2
    assert v1 != v3
    with pytest.raises(TypeError):
        {v1}  # noqa
    assert {v3, v4} == {v3}

    # exceptions in general compare by identity
    exc1 = RuntimeError('oops')
    exc2 = KeyError('foo')
    e1 = outcomes.Error(exc1)
    e2 = outcomes.Error(exc1)
    e3 = outcomes.Error(exc2)
    e4 = outcomes.Error(exc2)
    assert e1 == e2
    assert e3 == e4
    assert e1 != e3
    assert {e1, e2, e3, e4} == {e1, e3}


def test_value_compare():
    assert outcomes.Value(1) < outcomes.Value(2)
    assert not outcomes.Value(3) < outcomes.Value(2)
    with pytest.raises(TypeError):
        outcomes.Value(1) < outcomes.Value('foo')  # type: ignore  # noqa


def test_capture():
    def add(x, y):
        return x + y

    v = outcomes.capture(add, 2, y=3)
    assert type(v) is outcomes.Value
    assert v.unwrap() == 5

    def raise_value_error(x):
        raise ValueError(x)

    e = outcomes.capture(raise_value_error, 'two')
    assert type(e) is outcomes.Error
    assert type(e.error()) is ValueError
    assert e.error().args == ('two',)


def test_inheritance():
    assert issubclass(outcomes.Value, outcomes.Outcome)
    assert issubclass(outcomes.Error, outcomes.Outcome)


def test_traceback_frame_removal():
    def raise_value_error(x):
        raise ValueError(x)

    e = outcomes.capture(raise_value_error, 'abc')
    with pytest.raises(ValueError) as exc_info:  # noqa
        e.unwrap()
    frames = traceback.extract_tb(exc_info.value.__traceback__)
    functions = [function for _, _, function, _ in frames]
    assert functions[-2:] == ['unwrap', 'raise_value_error']


def test_error_unwrap_does_not_create_reference_cycles():
    # See comment in Error.unwrap for why reference cycles are tricky
    exc = ValueError()
    err = outcomes.Error(exc)
    try:
        err.unwrap()
    except ValueError:
        pass
    # Top frame in the traceback is the current test function; we don't care
    # about its references
    assert exc.__traceback__.tb_frame is sys._getframe()  # type: ignore  # noqa
    # The next frame down is the 'unwrap' frame; we want to make sure it
    # doesn't reference the exception (or anything else for that matter, just
    # to be thorough)
    unwrap_frame = exc.__traceback__.tb_next.tb_frame  # type: ignore
    assert unwrap_frame.f_code.co_name == 'unwrap'
    assert unwrap_frame.f_locals == {}


##


def test_acapture():
    async def run():
        async def add(x, y):
            await asyncio.sleep(0)
            return x + y

        v = await outcomes.acapture(add, 3, y=4)
        assert v == outcomes.Value(7)

        async def raise_value_error(x):
            await asyncio.sleep(0)
            raise ValueError(x)

        e = await outcomes.acapture(raise_value_error, 9)
        assert type(e.error()) is ValueError
        assert e.error().args == (9,)

    asyncio.run(run())


def test_asend():
    async def run():
        async def my_agen_func():
            assert (yield 1) == 'value'
            with pytest.raises(KeyError):
                yield 2
            yield 3

        my_agen = my_agen_func().__aiter__()
        v = outcomes.Value('value')
        e = outcomes.Error(KeyError())
        assert (await my_agen.asend(None)) == 1
        assert (await v.asend(my_agen)) == 2
        with pytest.raises(outcomes.OutcomeAlreadyUnwrappedError):
            await v.asend(my_agen)

        assert (await e.asend(my_agen)) == 3
        with pytest.raises(outcomes.OutcomeAlreadyUnwrappedError):
            await e.asend(my_agen)
        with pytest.raises(StopAsyncIteration):
            await my_agen.asend(None)

    asyncio.run(run())


def test_async_traceback_frame_removal():
    async def run():
        async def raise_value_error(x):
            raise ValueError(x)

        e = await outcomes.acapture(raise_value_error, 'abc')
        with pytest.raises(ValueError) as exc_info:  # noqa
            e.unwrap()
        frames = traceback.extract_tb(exc_info.value.__traceback__)
        functions = [function for _, _, function, _ in frames]
        assert functions[-2:] == ['unwrap', 'raise_value_error']

    asyncio.run(run())
