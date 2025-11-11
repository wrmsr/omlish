import pytest  # noqa

from omlish import inject as inj
from omlish import lang

from ..... import minichain as mc
from ....state.storage import InMemoryStateStorage
from ....state.storage import StateStorage
from ..chat.user.configs import UserConfig
from ....rendering.configs import RenderingConfig
from ..configs import ChatConfig
from ..chat.state.configs import StateConfig
from ..driver import ChatDriver
from ..inject import bind_chat


@mc.static_check_is_chat_choices_service
class DummyChatChoicesService:
    async def invoke(self, request: 'mc.ChatChoicesRequest') -> 'mc.ChatChoicesResponse':
        return mc.ChatChoicesResponse([mc.AiChoice([mc.AiMessage(f'*Ai Message {len(request.v) + 1}*')])])


def make_driver(
        cfg: ChatConfig = ChatConfig(),
) -> ChatDriver:
    injector = inj.create_injector(
        bind_chat(cfg),

        inj.bind(mc.ChatChoicesService, to_ctor=DummyChatChoicesService),

        inj.bind(InMemoryStateStorage, singleton=True),
        inj.bind(StateStorage, to_key=InMemoryStateStorage),
    )

    return injector[ChatDriver]


def test_inject():
    assert make_driver(
        cfg=ChatConfig(
            user=UserConfig(
                initial_user_content='Hi!',
            ),
            state=StateConfig(
                state='new',
            ),
        ),
    )


@pytest.mark.skip
def test_driver():
    lang.sync_await(make_driver(
        cfg=ChatConfig(
            user=UserConfig(
                initial_user_content='Hi!',
            ),
            rendering=RenderingConfig(
                markdown=True,
            ),
            state=StateConfig(
                state='new',
            ),
        ),
    ).run())
