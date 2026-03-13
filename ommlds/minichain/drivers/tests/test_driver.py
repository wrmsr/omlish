import uuid

import pytest  # noqa

from omlish import inject as inj
from omlish import lang

from ...chat.choices.services import ChatChoicesRequest
from ...chat.choices.services import ChatChoicesResponse
from ...chat.choices.services import ChatChoicesService
from ...chat.choices.services import static_check_is_chat_choices_service
from ...chat.choices.types import AiChoice
from ...chat.messages import AiMessage
from ..configs import DriverConfig
from ..inject import bind_driver
from ..state.inmemory import InMemoryStateManager
from ..state.types import ChatId
from ..state.types import StateManager
from ..types import Driver
from ..user.configs import UserConfig


@static_check_is_chat_choices_service
class DummyChatChoicesService:
    async def invoke(self, request: ChatChoicesRequest) -> ChatChoicesResponse:
        return ChatChoicesResponse([AiChoice([AiMessage(f'*Ai Message {len(request.v) + 1}*')])])


def make_driver(
        cfg: DriverConfig = DriverConfig(),
) -> Driver:
    injector = inj.create_injector(
        bind_driver(cfg),

        inj.bind(ChatChoicesService, to_ctor=DummyChatChoicesService),

        inj.bind(InMemoryStateManager, singleton=True),
        inj.bind(StateManager, to_key=InMemoryStateManager),

        inj.bind(ChatId(uuid.uuid4())),
    )

    return injector[Driver]


def test_inject():
    assert make_driver(
        cfg=DriverConfig(
            user=UserConfig(
                initial_user_content='Hi!',
            ),
        ),
    )


def test_driver():
    driver = make_driver(
        cfg=DriverConfig(
            user=UserConfig(
                initial_user_content='Hi!',
            ),
        ),
    )
    lang.sync_await(driver.start())
    lang.sync_await(driver.stop())
