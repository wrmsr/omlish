import os.path
import typing as ta
import uuid

import pytest

from omcore import check
from omcore import inject as inj
from omcore.http import all as http
from omcore.secrets.tests.harness import HarnessSecrets

from .....backends.openai.stream import OpenaiChatChoicesStreamService
from .....chat.messages import UserMessage
from .....chat.stream.choices.services import ChatChoicesStreamService
from .....events.injection import event_callbacks
from .....events.types import Event
from .....fs.types import FsRoot
from .....modules.code.configs import CodeConfig
from .....modules.fs.configs import FsConfig
from .....modules.inject import bind_module
from .....standard import ApiKey
from .....tools.execution.permissions import DecidedToolPermissionState
from .....tools.execution.permissions import ToolPermissionDecider
from .....tools.permissions.fs import FsToolPermissionTarget
from .....tools.permissions.managers import ToolPermissionsManager  # noqa
from .....tools.permissions.types import ToolPermissionState  # noqa
from .....tools.permissions.types import ToolPermissionTarget
from ....actions import SendUserMessagesAction
from ....ai.configs import AiConfig
from ....configs import DriverConfig
from ....inject import bind_driver
from ....storage.types import ChatId
from ....types import Driver


def bind_openai_driver(
        svc: OpenaiChatChoicesStreamService,
        cfg: DriverConfig = DriverConfig(),
) -> inj.Elements:
    els: list[inj.Elemental] = []

    els.extend([
        bind_driver(cfg),

        inj.bind(svc),
        inj.bind(ChatChoicesStreamService, to_key=OpenaiChatChoicesStreamService),

        inj.bind(ChatId(uuid.uuid7())),
    ])

    return inj.as_elements(*els)


# class MyToolPermissionsManager(ToolPermissionsManager):
#     pass


FS_ROOT = FsRoot(os.path.abspath(os.path.dirname(__file__)))


class MyToolPermissionDecider(ToolPermissionDecider):
    async def decide(self, target: ToolPermissionTarget) -> DecidedToolPermissionState | None:
        fs_pt = check.isinstance(target, FsToolPermissionTarget)  # noqa

        return ToolPermissionState.DENY


@pytest.mark.online
@pytest.mark.asyncs('asyncio')
async def test_fizzbuzz(harness):
    llm = OpenaiChatChoicesStreamService(
        ApiKey(harness[HarnessSecrets].get_or_skip('openai_api_key').reveal()),
        http_client=http.SyncAsyncHttpClient(http.client()),
    )

    async def on_event(event: Event) -> None:
        print(event)

    els: list[ta.Any] = [
        inj.bind(FsRoot, to_const=FS_ROOT),

        inj.bind(MyToolPermissionDecider, singleton=True),

        inj.override(
            bind_openai_driver(
                llm,
                cfg=DriverConfig(
                    ai=AiConfig(
                        stream=True,
                        enable_tools=True,
                    ),
                ),
            ),

            inj.bind(ToolPermissionDecider, to_key=MyToolPermissionDecider),
        ),

        bind_module(CodeConfig()),
        bind_module(FsConfig()),

        event_callbacks().bind_item(to_const=on_event),
    ]

    async with inj.create_async_managed_injector(*els) as injector:
        driver = await injector[Driver]
        assert driver

        await driver.start()

        await driver.do_action(SendUserMessagesAction([
            UserMessage("There's a bug in the file 'fizzbuzz.py' - can you find it?"),
        ]))
