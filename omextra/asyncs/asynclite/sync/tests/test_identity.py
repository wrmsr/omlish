import threading

from omlish.testing.unittest.asyncs import SyncIsolatedAsyncTestCase

from ..identity import SyncAsyncliteIdentity


class TestSyncIdentity(SyncIsolatedAsyncTestCase):
    async def test_current_identity_returns_thread(self):
        api = SyncAsyncliteIdentity()
        identity = api.current_identity()

        # Should return the current thread
        self.assertIsNotNone(identity)
        self.assertIsInstance(identity, threading.Thread)

    async def test_current_identity_is_consistent(self):
        api = SyncAsyncliteIdentity()

        identity1 = api.current_identity()
        identity2 = api.current_identity()

        # Same thread should return same identity
        self.assertIs(identity1, identity2)

    async def test_different_threads_have_different_identities(self):
        api = SyncAsyncliteIdentity()
        identities = []
        ready = threading.Event()
        done = threading.Event()

        def get_identity():
            identities.append(api.current_identity())
            ready.set()
            done.wait()

        main_identity = api.current_identity()

        thread = threading.Thread(target=get_identity)
        thread.start()
        ready.wait()

        # Main thread and created thread should have different identities
        self.assertEqual(len(identities), 1)
        self.assertIsNot(main_identity, identities[0])

        done.set()
        thread.join()
