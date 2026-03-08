from omlish import check
from omlish import inject as inj
from omlish import lang

from ...... import minichain as mc
from ..inject import system_message_providers
from ..phases.injection import phase_callbacks
from ..phases.types import ChatPhase
from ..phases.types import ChatPhaseCallback
from .configs import UserConfig


with lang.auto_proxy_import(globals()):
    from .. import types as _driver
    from . import preparing as _preparing


##


def bind_user(cfg: UserConfig = UserConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    if cfg.initial_system_content is not None:
        els.extend([
            inj.bind(_preparing.InitialSystemMessageProvider(cfg.initial_system_content)),
            system_message_providers().bind_item(to_key=_preparing.InitialSystemMessageProvider),
        ])

    if cfg.initial_user_content is not None:
        async def add_initial_user_content(cdg: '_driver.ChatDriverGetter') -> None:
            await (await cdg()).send_user_messages([mc.UserMessage(check.not_none(cfg.initial_user_content))])

        els.append(phase_callbacks().bind_item(to_fn=inj.KwargsTarget.of(
            lambda cdg: ChatPhaseCallback(ChatPhase.STARTED, lambda: add_initial_user_content(cdg)),
            cdg=_driver.ChatDriverGetter,
        )))

    return inj.as_elements(*els)
