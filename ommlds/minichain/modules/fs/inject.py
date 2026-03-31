import os

from omlish import inject as inj
from omlish import lang

from ...drivers.tools.injection import bind_tool_context_provider_to_key
from ...drivers.tools.injection import tool_catalog_entries
from .configs import FsConfig


with lang.auto_proxy_import(globals()):
    from . import context as _context
    from .tools import edit as _edit
    from .tools import ls as _ls
    from .tools import read as _read


##


def bind_fs(cfg: FsConfig = FsConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.extend([
        inj.bind(_context.FsContext(
            root_dir=os.getcwd(),  # FIXME: lol
        )),
        bind_tool_context_provider_to_key(_context.FsContext),
    ])

    #

    els.append(
        tool_catalog_entries().bind_item_consts(
            _ls.ls_tool(),
            _read.read_tool(),
        ),
    )

    #

    if cfg.enable_writes:
        els.append(
            tool_catalog_entries().bind_item_consts(
                _edit.edit_tool(),
            ),
        )

    #

    return inj.as_elements(*els)
