import unittest

import anyio

from ..events import AnyioAsyncliteEvents


def run_anyio_test(test_fn):
    """Helper to run an async test function with anyio."""

    anyio.run(test_fn)


class TestAnyioEvents(unittest.TestCase):
    def test_initial_state(self):
        async def _test():
            api = AnyioAsyncliteEvents()
            event = api.make_event()

            self.assertFalse(event.is_set())

        run_anyio_test(_test)

    def test_set_and_is_set(self):
        async def _test():
            api = AnyioAsyncliteEvents()
            event = api.make_event()

            self.assertFalse(event.is_set())

            event.set()
            self.assertTrue(event.is_set())

        run_anyio_test(_test)

    def test_wait_when_set(self):
        async def _test():
            api = AnyioAsyncliteEvents()
            event = api.make_event()

            event.set()
            await event.wait()

            self.assertTrue(event.is_set())

        run_anyio_test(_test)

    def test_wait_blocks_until_set(self):
        async def _test():
            api = AnyioAsyncliteEvents()
            event = api.make_event()
            result = []

            async def waiter():
                result.append('waiting')
                await event.wait()
                result.append('done')

            async with anyio.create_task_group() as tg:
                tg.start_soon(waiter)
                await anyio.sleep(0.01)

                self.assertEqual(result, ['waiting'])
                self.assertFalse(event.is_set())

                event.set()

            self.assertEqual(result, ['waiting', 'done'])
            self.assertTrue(event.is_set())

        run_anyio_test(_test)

    def test_wait_timeout(self):
        async def _test():
            api = AnyioAsyncliteEvents()
            event = api.make_event()

            self.assertFalse(event.is_set())

            with self.assertRaises(TimeoutError):
                await event.wait(timeout=0.1)

            self.assertFalse(event.is_set())

        run_anyio_test(_test)

    def test_multiple_waiters(self):
        async def _test():
            api = AnyioAsyncliteEvents()
            event = api.make_event()
            results = []

            async def waiter(name: str):
                await event.wait()
                results.append(name)

            async with anyio.create_task_group() as tg:
                tg.start_soon(waiter, 'first')
                tg.start_soon(waiter, 'second')
                tg.start_soon(waiter, 'third')

                await anyio.sleep(0.01)
                self.assertEqual(results, [])

                event.set()

            self.assertEqual(sorted(results), ['first', 'second', 'third'])

        run_anyio_test(_test)

    def test_set_is_idempotent(self):
        async def _test():
            api = AnyioAsyncliteEvents()
            event = api.make_event()

            event.set()
            self.assertTrue(event.is_set())

            event.set()
            self.assertTrue(event.is_set())

            await event.wait()
            self.assertTrue(event.is_set())

        run_anyio_test(_test)
