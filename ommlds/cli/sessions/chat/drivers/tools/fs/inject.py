import os

from omlish import inject as inj

from ..injection import ToolSetBinder
from ..injection import bind_tool_context_provider_to_key
from ..injection import tool_catalog_entries
from .configs import FsToolSetConfig


##


def bind_fs_tools(cfg: FsToolSetConfig) -> inj.Elements:
    from ......minichain.lib.fs.context import FsContext
    from ......minichain.lib.fs.tools.ls import ls_tool
    from ......minichain.lib.fs.tools.read import read_tool

    return inj.as_elements(
        tool_catalog_entries().bind_item_consts(
            ls_tool(),
            read_tool(),
        ),

        inj.bind(FsContext(
            root_dir=os.getcwd(),
        )),
        bind_tool_context_provider_to_key(FsContext),
    )


##


FS_TOOL_SET_BINDER = ToolSetBinder(FsToolSetConfig, bind_fs_tools)
