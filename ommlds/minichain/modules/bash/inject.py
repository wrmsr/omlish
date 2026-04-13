import os

from omlish import inject as inj
from omlish import lang

from ...drivers.tools.injection import bind_tool_context_provider_to_key
from ...drivers.tools.injection import tool_catalog_entries
from .configs import BashConfig


with lang.auto_proxy_import(globals()):
    from . import bash as _bash
    from . import context as _context


##


def bind_bash(cfg: BashConfig = BashConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.extend([
        inj.bind(_context.BashContext(
            root_dir=os.getcwd(),  # FIXME: lol
        )),
        bind_tool_context_provider_to_key(_context.BashContext),
    ])

    #

    els.append(
        tool_catalog_entries().bind_item_consts(
            _bash.bash_tool(),
        ),
    )

    #

    return inj.as_elements(*els)
