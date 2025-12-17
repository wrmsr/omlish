import contextlib

import pytest  # noqa

from omlish import inject as inj
from omlish import lang

from ..... import minichain as mc
from ....backends.types import ChatChoicesServiceBackendProvider
from ....rendering.configs import RenderingConfig
from ....state.storage import InMemoryStateStorage
from ....state.storage import StateStorage
from ..configs import ChatConfig
from ..drivers.configs import DriverConfig
from ..drivers.driver import ChatDriver
from ..drivers.state.configs import StateConfig
from ..drivers.user.configs import UserConfig
from ..inject import bind_chat


@mc.static_check_is_chat_choices_service
class DummyChatChoicesService:
    async def invoke(self, request: 'mc.ChatChoicesRequest') -> 'mc.ChatChoicesResponse':
        return mc.ChatChoicesResponse([mc.AiChoice([mc.AiMessage(f'*Ai Message {len(request.v) + 1}*')])])


class DummyChatChoicesServiceBackendProvider(ChatChoicesServiceBackendProvider):
    @contextlib.asynccontextmanager
    async def provide_backend(self):
        yield DummyChatChoicesService()


def make_driver(
        cfg: ChatConfig = ChatConfig(),
) -> ChatDriver:
    injector = inj.create_injector(
        inj.override(
            bind_chat(cfg),

            inj.bind(ChatChoicesServiceBackendProvider, to_ctor=DummyChatChoicesServiceBackendProvider),
        ),

        inj.bind(InMemoryStateStorage, singleton=True),
        inj.bind(StateStorage, to_key=InMemoryStateStorage),
    )

    return injector[ChatDriver]


def test_inject():
    assert make_driver(
        cfg=ChatConfig(
            driver=DriverConfig(
                user=UserConfig(
                    initial_user_content='Hi!',
                ),
                state=StateConfig(
                    state='new',
                ),
            ),
        ),
    )


def test_driver():
    driver = make_driver(
        cfg=ChatConfig(
            driver=DriverConfig(
                user=UserConfig(
                    initial_user_content='Hi!',
                ),
                state=StateConfig(
                    state='new',
                ),
            ),
            rendering=RenderingConfig(
                markdown=True,
            ),
        ),
    )
    lang.sync_await(driver.start())
    lang.sync_await(driver.stop())
