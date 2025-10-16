from omlish import inject as inj

import pytest

from ..configs import ChatConfig
from ..driver import ChatDriver
from ..inject import bind_chat


def make_driver(cfg: ChatConfig | None = None) -> ChatDriver:
    injector = inj.create_injector(bind_chat(cfg or ChatConfig()))
    return injector[ChatDriver]


def test_inject():
    assert make_driver()


@pytest.mark.asyncs('asyncio')
async def test_driver():
    await make_driver().run()
