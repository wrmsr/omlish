# @omlish-lite
import asyncio

from omlish.testing.unittest.asyncs import AsyncioIsolatedAsyncTestCase

from ..identities import AsyncioAsyncliteIdentities


class TestAsyncioIdentities(AsyncioIsolatedAsyncTestCase):
    async def test_current_identity_returns_task(self):
        api = AsyncioAsyncliteIdentities()
        identity = api.current_identity()

        # Should return the current task
        self.assertIsNotNone(identity)
        self.assertIsInstance(identity, asyncio.Task)

    async def test_current_identity_is_consistent(self):
        api = AsyncioAsyncliteIdentities()

        identity1 = api.current_identity()
        identity2 = api.current_identity()

        # Same task should return same identity
        self.assertIs(identity1, identity2)

    async def test_different_tasks_have_different_identities(self):
        api = AsyncioAsyncliteIdentities()
        identities = []

        async def get_identity():
            identities.append(api.current_identity())

        main_identity = api.current_identity()

        task = asyncio.create_task(get_identity())
        await task

        # Main task and created task should have different identities
        self.assertEqual(len(identities), 1)
        self.assertIsNot(main_identity, identities[0])
