"""
Real (no-mock) wiring helpers for driver-level tests: a fully-wired driver over the scripted backend, optionally on a
real sqlite file for multi-session scenarios. Not a test module itself - this is the supported way to write offline
end-to-end driver tests (see `drivers/tests/test_scripted.py` for usage).
"""
import uuid

from omlish import dataclasses as dc
from omlish import inject as inj

from ..backends.scripted.chat import ScriptedChatChoicesService
from ..backends.scripted.chat import ScriptedChatChoicesStreamService
from ..backends.scripted.chat import ScriptedChatScript
from ..backends.scripted.scripts import ChatScript
from ..chat.choices.services import ChatChoicesService
from ..chat.choices.stream.services import ChatChoicesStreamService
from ..tools.execution.permissions import DecidedToolPermissionState
from ..tools.execution.permissions import ToolPermissionDecider
from ..tools.permissions.types import ToolPermissionState
from ..tools.permissions.types import ToolPermissionTarget
from .configs import DriverConfig
from .inject import bind_driver
from .orm.configs import OrmConfig
from .storage.types import ChatId


##


class AllowAllToolPermissionDecider(ToolPermissionDecider):
    async def decide(self, target: ToolPermissionTarget) -> DecidedToolPermissionState:
        return ToolPermissionState.ALLOW


##


def bind_scripted_driver(
        script: ChatScript,
        cfg: DriverConfig = DriverConfig(),
        *,
        chat_id: ChatId | None = None,
        db_file_path: str | None = None,
) -> inj.Elements:
    """
    A complete driver wired to the scripted backend (stream or not per `cfg.ai.stream`), with allow-all tool
    permissions. Pass a sqlite `db_file_path` (and a fixed `chat_id`) to simulate multi-session scenarios - note that
    `orm.InMemoryStore` (the default) cannot be shared across injectors, as its tables key on mapper identity.
    """

    if db_file_path is not None:
        cfg = dc.replace(cfg, orm=OrmConfig(file_path=db_file_path))

    els: list[inj.Elemental] = []

    overrides: list[inj.Elemental] = [
        inj.bind(ToolPermissionDecider, to_key=AllowAllToolPermissionDecider),
    ]

    if cfg.ai.stream:
        svc_els = inj.as_elements(
            inj.bind(
                ScriptedChatChoicesStreamService,
                to_const=ScriptedChatChoicesStreamService(ScriptedChatScript(script)),
            ),
            inj.bind(ChatChoicesStreamService, to_key=ScriptedChatChoicesStreamService),
        )
    else:
        svc_els = inj.as_elements(
            inj.bind(
                ScriptedChatChoicesService,
                to_const=ScriptedChatChoicesService(ScriptedChatScript(script)),
            ),
            inj.bind(ChatChoicesService, to_key=ScriptedChatChoicesService),
        )

    els.extend([
        inj.bind(AllowAllToolPermissionDecider, singleton=True),

        inj.override(
            inj.as_elements(
                bind_driver(cfg),

                svc_els,
            ),

            *overrides,
        ),

        inj.bind(chat_id if chat_id is not None else ChatId(uuid.uuid7())),
    ])

    return inj.as_elements(*els)
