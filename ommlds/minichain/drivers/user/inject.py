from omlish import check
from omlish import inject as inj

from ...chat.messages import UserMessage
from ..inject import system_message_providers
from ..phases.injection import phase_callbacks
from ..phases.types import ChatPhase
from ..phases.types import ChatPhaseCallback
from ..types import ChatDriverGetter
from .configs import UserConfig
from .preparing import InitialSystemMessageProvider


##


def bind_user(cfg: UserConfig = UserConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    if cfg.initial_system_content is not None:
        els.extend([
            inj.bind(InitialSystemMessageProvider(cfg.initial_system_content)),
            system_message_providers().bind_item(to_key=InitialSystemMessageProvider),
        ])

    if cfg.initial_user_content is not None:
        async def add_initial_user_content(cdg: ChatDriverGetter) -> None:
            await (await cdg()).send_user_messages([UserMessage(check.not_none(cfg.initial_user_content))])

        els.append(phase_callbacks().bind_item(to_fn=inj.KwargsTarget.of(
            lambda cdg: ChatPhaseCallback(ChatPhase.STARTED, lambda: add_initial_user_content(cdg)),
            cdg=ChatDriverGetter,
        )))

    return inj.as_elements(*els)
