import anyio

from omlish.testing.unittest.asyncs import AnyioIsolatedAsyncTestCase

from ..identity import AnyioAsyncliteIdentity


class TestAnyioIdentity(AnyioIsolatedAsyncTestCase):
    async def test_current_identity_returns_task_info(self):
        api = AnyioAsyncliteIdentity()
        identity = api.current_identity()

        # Should return the current task info
        self.assertIsNotNone(identity)
        self.assertIsInstance(identity, anyio.TaskInfo)

    async def test_current_identity_is_consistent(self):
        api = AnyioAsyncliteIdentity()

        identity1 = api.current_identity()
        identity2 = api.current_identity()

        # Same task should return same identity (or at least equal identity)
        self.assertEqual(identity1.id, identity2.id)

    async def test_different_tasks_have_different_identities(self):
        api = AnyioAsyncliteIdentity()
        identities = []

        async def get_identity():
            identities.append(api.current_identity())

        main_identity = api.current_identity()

        async with anyio.create_task_group() as tg:
            tg.start_soon(get_identity)

        # Main task and created task should have different identities
        self.assertEqual(len(identities), 1)
        self.assertNotEqual(main_identity.id, identities[0].id)
