from omlish.argparse import all as argparse

from ......minichain.tools.execution.catalog import ToolCatalog
from .base import Command


##


class ToolsCommand(Command):
    def __init__(
            self,
            *,
            tool_catalog: ToolCatalog,
    ) -> None:
        super().__init__()

        self._tool_catalog = tool_catalog

    async def _run_args(self, ctx: Command.Context, args: argparse.Namespace) -> None:
        await ctx.print('\n'.join(sorted(self._tool_catalog.by_name)))
