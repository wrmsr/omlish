import typing as ta

import pytest

from omlish import inject as inj

from ....state import InMemoryStateStorage
from ....state import StateStorage
from ..configs import ChatConfig
from ..driver import ChatDriver
from ..inject import bind_chat


def make_driver(
        cfg: ChatConfig | None = None,
        **kwargs: ta.Any,
) -> ChatDriver:
    if cfg is not None:
        assert not kwargs
    else:
        cfg = ChatConfig(**kwargs)

    injector = inj.create_injector(
        bind_chat(cfg),

        inj.bind(InMemoryStateStorage, singleton=True),
        inj.bind(StateStorage, to_key=InMemoryStateStorage),
    )

    return injector[ChatDriver]


def test_inject():
    assert make_driver(
        state='new',
    )


@pytest.mark.asyncs('asyncio')
async def test_driver():
    await make_driver(
        state='new',
    ).run()
