from omlish import inject as inj
from omlish import lang

from ...drivers.tools.injection import bind_tool_context_provider_to_key
from ...drivers.tools.injection import tool_catalog_entries
from .configs import TodoConfig


with lang.auto_proxy_import(globals()):
    from . import context as _context
    from .tools import read as _read
    from .tools import write as _write


##


def bind_todo(cfg: TodoConfig = TodoConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.extend([
        tool_catalog_entries().bind_item_consts(
            _read.todo_read_tool(),
            _write.todo_write_tool(),
        ),

        inj.bind(_context.TodoContext()),
        bind_tool_context_provider_to_key(_context.TodoContext),
    ])

    #

    return inj.as_elements(*els)
