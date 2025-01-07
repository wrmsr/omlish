"""
TODO:
 - contextvars
  - https://github.com/python-greenlet/greenlet/commit/f9c824152bed2a70d94283928389f88b4dc46638
"""
import asyncio
import functools

from ...testing import pytest as ptu


@ptu.skip.if_cant_import('greenlet')
def test_greenlet():
    import greenlet

    done = 0

    def test1():
        gr2.switch()
        gr2.switch()
        nonlocal done
        done += 1

    def test2():
        def f():
            gr1.switch()
        f()
        nonlocal done
        done += 1
        gr1.switch()

    gr1 = greenlet.greenlet(test1)
    gr2 = greenlet.greenlet(test2)
    gr1.switch()
    assert done == 2


@ptu.skip.if_cant_import('greenlet')
def test_bridge():
    import greenlet

    l = []

    async def gl_async(fn, *args, **kwargs):
        let = greenlet.greenlet(functools.partial(fn, *args, **kwargs))
        awaitable = let.switch()
        result = await awaitable
        ret = let.switch(result)
        assert let.dead
        return ret

    def gl_await(awaitable):
        return greenlet.getcurrent().parent.switch(awaitable)

    def f(sleepfor) -> int:
        gl_await(asyncio.sleep(sleepfor))
        return 4

    async def hello(name, sleepfor) -> int:
        l.append(f'start {name}')
        x = await gl_async(f, sleepfor)
        l.append(f'end {name}')
        return x

    async def main():
        rs = await asyncio.gather(
            hello('Billy Bob', .3),
            hello('Billy Alice', .1),
        )
        assert rs == [4, 4]

    with asyncio.Runner() as runner:
        runner.get_loop().run_until_complete(main())  # noqa
