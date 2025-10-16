import typing as ta

import pytest

from omlish import inject as inj

from ..... import minichain as mc
from ....state import InMemoryStateStorage
from ....state import StateStorage
from ..chat.ai.types import AiChatGenerator
from ..configs import ChatConfig
from ..driver import ChatDriver
from ..inject import bind_chat


class DummyAiChatGenerator(AiChatGenerator):
    async def get_next_ai_messages(self, chat: mc.Chat) -> mc.AiChat:
        return [mc.AiMessage(f'Ai Message #{len(chat) + 1}')]


def make_driver(
        cfg: ChatConfig | None = None,
        **kwargs: ta.Any,
) -> ChatDriver:
    if cfg is not None:
        assert not kwargs
    else:
        cfg = ChatConfig(**kwargs)

    injector = inj.create_injector(
        inj.override(
            bind_chat(cfg),
            inj.bind(AiChatGenerator, to_key=DummyAiChatGenerator),
        ),

        inj.bind(DummyAiChatGenerator),

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
        initial_content='Hi!',
    ).run()
