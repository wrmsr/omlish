# @omlish-lite
import unittest

from .. import all as bl


class TestDelegation(unittest.TestCase):
    def test_delegation(self):
        def child():
            print('Child started.')
            yield bl.null()
            print('Child resumed.')
            yield bl.null()
            print('Child ending.')
            yield bl.end(42)

        def parent():
            print('Parent started.')
            yield bl.null()
            print('Parent resumed.')
            result = yield child()
            print('Child returned:', repr(result))
            print('Parent ending.')

        def exc_child():
            yield bl.null()
            raise Exception

        def exc_parent():
            try:
                yield exc_child()
            except Exception as exc:  # noqa
                print('Parent caught:', repr(exc))

        def exc_grandparent():
            yield bl.spawn(exc_parent())

        bl.run(parent())
        bl.run(exc_grandparent())

    def test_sleepy(self):
        def sleeper(duration: float) -> bl.Coro:
            print(f'Going to sleep for {duration} seconds...')
            yield bl.sleep(duration)
            print(f'...woke up after {duration} seconds.')

        def sleepy() -> bl.Coro:
            for i in (0, .1, .3, .5):
                yield bl.spawn(sleeper(i))

        bl.run(sleepy())
