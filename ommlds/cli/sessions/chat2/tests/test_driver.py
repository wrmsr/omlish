import typing as ta

import pytest  # noqa

from omlish import lang
from omlish import inject as inj

from ..... import minichain as mc
from ....state import InMemoryStateStorage
from ....state import StateStorage
from ..configs import ChatConfig
from ..driver import ChatDriver
from ..inject import bind_chat


@mc.static_check_is_chat_choices_service
class DummyChatChoicesService:
    async def invoke(self, request: mc.ChatChoicesRequest) -> mc.ChatChoicesResponse:
        return mc.ChatChoicesResponse([mc.AiChoice([mc.AiMessage(f'Ai Message *#{len(request.v) + 1}*')])])


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

        inj.bind(mc.ChatChoicesService, to_ctor=DummyChatChoicesService),

        inj.bind(InMemoryStateStorage, singleton=True),
        inj.bind(StateStorage, to_key=InMemoryStateStorage),
    )

    return injector[ChatDriver]


def test_inject():
    assert make_driver(
        state='new',
        initial_content='Hi!',
    )


def test_driver():
    lang.sync_await(make_driver(
        state='new',
        initial_content='Hi!',
        markdown=True,
    ).run())
