from omlish import inject as inj
from omlish import lang

from ...drivers.injection import system_message_providers
from ...drivers.preparing.types import ProvidedSystemMessage
from ...drivers.preparing.types import StaticSystemMessageProvider
from ...tools.execution.injection import bind_tool_context_provider_to_key
from ...tools.execution.injection import tool_catalog_entries
from .configs import FsConfig


with lang.auto_proxy_import(globals()):
    from . import context as _context
    from . import prompts as _prompts
    from .tools import edit as _edit
    from .tools import ls as _ls
    from .tools import read as _read
    from .tools import write as _write


##


def bind_fs(cfg: FsConfig = FsConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.extend([
        inj.bind(_context.FsContext, singleton=True),
        bind_tool_context_provider_to_key(_context.FsContext),
    ])

    #

    els.extend([
        tool_catalog_entries().bind_item_consts(
            _ls.ls_tool(),
            _read.read_tool(),
        ),

        system_message_providers().bind_item_consts(StaticSystemMessageProvider([ProvidedSystemMessage(
            _prompts.READ_SYSTEM_PROMPT,
        )])),
    ])

    #

    if cfg.enable_writes:
        els.extend([
            tool_catalog_entries().bind_item_consts(
                _edit.edit_tool(),
                _write.write_tool(),
            ),

            system_message_providers().bind_item_consts(StaticSystemMessageProvider([ProvidedSystemMessage(
                _prompts.WRITE_SYSTEM_PROMPT,
            )])),
        ])

    #

    return inj.as_elements(*els)
