import uuid

import pytest  # noqa

from omlish import inject as inj

from ...chat.choices.services import ChatChoicesRequest
from ...chat.choices.services import ChatChoicesResponse
from ...chat.choices.services import ChatChoicesService
from ...chat.choices.services import static_check_is_chat_choices_service
from ...chat.choices.types import AiChoice
from ...chat.messages import AiMessage
from ..configs import DriverConfig
from ..inject import bind_driver
from ..state.types import ChatId
from ..types import Driver
from ..user.configs import UserConfig


@static_check_is_chat_choices_service
class DummyChatChoicesService:
    async def invoke(self, request: ChatChoicesRequest) -> ChatChoicesResponse:
        return ChatChoicesResponse([AiChoice([AiMessage(f'*Ai Message {len(request.v) + 1}*')])])


def bind_test_driver(
        cfg: DriverConfig = DriverConfig(),
) -> inj.Elements:
    els: list[inj.Elemental] = []

    els.extend([
        bind_driver(cfg),

        inj.bind(ChatChoicesService, to_ctor=DummyChatChoicesService),

        inj.bind(ChatId(uuid.uuid4())),
    ])

    return inj.as_elements(*els)


@pytest.mark.asyncs('asyncio')
async def test_inject():
    async with inj.create_async_managed_injector(bind_test_driver(
        cfg=DriverConfig(
            user=UserConfig(
                initial_user_content='Hi!',
            ),
        ),
    )) as injector:
        driver = await injector[Driver]
        assert driver


@pytest.mark.asyncs('asyncio')
async def test_driver():
    async with inj.create_async_managed_injector(bind_test_driver(
        cfg=DriverConfig(
            user=UserConfig(
                initial_user_content='Hi!',
            ),
        ),
    )) as injector:
        driver = await injector[Driver]

        await driver.start()
        await driver.stop()
