import contextlib

import pytest  # noqa

from omlish import inject as inj
from omlish import lang

from ..... import minichain as mc
from ....backends.types import ChatChoicesServiceBackendProvider
from ....rendering.configs import RenderingConfig
from ....state.storage import InMemoryStateStorage
from ....state.storage import StateStorage
from ..agents.agent import ChatAgent
from ..agents.configs import AgentConfig
from ..agents.state.configs import StateConfig
from ..agents.user.configs import UserConfig
from ..configs import ChatConfig
from ..inject import bind_chat


@mc.static_check_is_chat_choices_service
class DummyChatChoicesService:
    async def invoke(self, request: 'mc.ChatChoicesRequest') -> 'mc.ChatChoicesResponse':
        return mc.ChatChoicesResponse([mc.AiChoice([mc.AiMessage(f'*Ai Message {len(request.v) + 1}*')])])


class DummyChatChoicesServiceBackendProvider(ChatChoicesServiceBackendProvider):
    @contextlib.asynccontextmanager
    async def provide_backend(self):
        yield DummyChatChoicesService()


def make_agent(
        cfg: ChatConfig = ChatConfig(),
) -> ChatAgent:
    injector = inj.create_injector(
        inj.override(
            bind_chat(cfg),

            inj.bind(ChatChoicesServiceBackendProvider, to_ctor=DummyChatChoicesServiceBackendProvider),
        ),

        inj.bind(InMemoryStateStorage, singleton=True),
        inj.bind(StateStorage, to_key=InMemoryStateStorage),
    )

    return injector[ChatAgent]


def test_inject():
    assert make_agent(
        cfg=ChatConfig(
            agent=AgentConfig(
                user=UserConfig(
                    initial_user_content='Hi!',
                ),
                state=StateConfig(
                    state='new',
                ),
            ),
        ),
    )


def test_agent():
    agent = make_agent(
        cfg=ChatConfig(
            agent=AgentConfig(
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
    lang.sync_await(agent.start())
    lang.sync_await(agent.stop())
