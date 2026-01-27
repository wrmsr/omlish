from .....testing.unittest.asyncs import AnyioIsolatedAsyncTestCase
from ..sleeps import AnyioAsyncliteSleeps


class TestAnyio(AnyioIsolatedAsyncTestCase):
    async def test_sleep(self):
        await AnyioAsyncliteSleeps().sleep(.2)
