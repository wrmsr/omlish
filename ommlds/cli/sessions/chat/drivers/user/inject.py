from omlish import check
from omlish import inject as inj
from omlish import lang

from ...... import minichain as mc
from ..phases.injection import phase_callbacks
from ..phases.types import ChatPhase
from ..phases.types import ChatPhaseCallback
from .configs import UserConfig


with lang.auto_proxy_import(globals()):
    from .. import types as _driver
    from ..state import types as _state


##


def bind_user(cfg: UserConfig = UserConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    if cfg.initial_system_content is not None:
        async def add_initial_system_content(cm: '_state.ChatStateManager') -> None:
            await cm.extend_chat([mc.SystemMessage(check.not_none(cfg.initial_system_content))])

        els.append(phase_callbacks().bind_item(to_fn=inj.KwargsTarget.of(
            lambda cm: ChatPhaseCallback(ChatPhase.STARTED, lambda: add_initial_system_content(cm)),
            cm=_state.ChatStateManager,
        )))

    if cfg.initial_user_content is not None:
        async def add_initial_user_content(cdg: '_driver.ChatDriverGetter') -> None:
            await (await cdg()).send_user_messages([mc.UserMessage(check.not_none(cfg.initial_user_content))])

        els.append(phase_callbacks().bind_item(to_fn=inj.KwargsTarget.of(
            lambda cdg: ChatPhaseCallback(ChatPhase.STARTED, lambda: add_initial_user_content(cdg)),
            cdg=_driver.ChatDriverGetter,
        )))

    return inj.as_elements(*els)
