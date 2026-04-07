import uuid

import pytest

from omlish import inject as inj
from omlish.http import all as http
from omlish.secrets.tests.harness import HarnessSecrets

from ...backends.impls.openai.stream import OpenaiChatChoicesStreamService
from ...chat.choices.stream.services import ChatChoicesStreamService
from ...standard import ApiKey
from ..ai.configs import AiConfig
from ..configs import DriverConfig
from ..inject import bind_driver
from ..state.types import ChatId
from ..types import Driver
from ..user.configs import UserConfig


def bind_openai_driver(
        svc: OpenaiChatChoicesStreamService,
        cfg: DriverConfig = DriverConfig(),
) -> inj.Elements:
    els: list[inj.Elemental] = []

    els.extend([
        bind_driver(cfg),

        inj.bind(svc),
        inj.bind(ChatChoicesStreamService, to_key=OpenaiChatChoicesStreamService),

        inj.bind(ChatId(uuid.uuid4())),
    ])

    return inj.as_elements(*els)


@pytest.mark.online
@pytest.mark.asyncs('asyncio')
async def test_openai_chat_stream_model(harness):
    llm = OpenaiChatChoicesStreamService(
        ApiKey(harness[HarnessSecrets].get_or_skip('openai_api_key').reveal()),
        http_client=http.SyncAsyncHttpClient(http.client()),
    )

    async with inj.create_async_managed_injector(bind_openai_driver(
            llm,
            cfg=DriverConfig(
                ai=AiConfig(
                    stream=True,
                ),
                user=UserConfig(
                    initial_user_content='Hi!',
                ),
            ),
    )) as injector:
        driver = await injector[Driver]
        assert driver

        await driver.start()
