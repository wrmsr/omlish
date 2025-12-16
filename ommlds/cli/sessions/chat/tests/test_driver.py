import pytest  # noqa

from omlish import inject as inj
from omlish import lang

from ..... import minichain as mc
from ....state.storage import InMemoryStateStorage
from ....state.storage import StateStorage
from ..agents.configs import AgentConfig
from ..agents.user.configs import UserConfig
from ....rendering.configs import RenderingConfig
from ..configs import ChatConfig
from ..agents.state.configs import StateConfig
from ..agents.agent import ChatAgent
from ..inject import bind_chat


@mc.static_check_is_chat_choices_service
class DummyChatChoicesService:
    async def invoke(self, request: 'mc.ChatChoicesRequest') -> 'mc.ChatChoicesResponse':
        return mc.ChatChoicesResponse([mc.AiChoice([mc.AiMessage(f'*Ai Message {len(request.v) + 1}*')])])


def make_agent(
        cfg: ChatConfig = ChatConfig(),
) -> ChatAgent:
    injector = inj.create_injector(
        bind_chat(cfg),

        inj.bind(mc.ChatChoicesService, to_ctor=DummyChatChoicesService),

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


# @pytest.mark.skip
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
