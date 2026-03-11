from omlish.argparse import all as argparse

from ...... import minichain as mc
from ...facades.text import FacadeText
from .base import Command


##


class PermissionsCommand(Command):
    def __init__(self, permissions: 'mc.ToolPermissions') -> None:
        super().__init__()

        self._permissions = permissions

    async def _run_args(self, ctx: Command.Context, args: argparse.Namespace) -> None:
        dct = self._permissions.get_tool_permission_states()
        if not dct:
            await ctx.print('No permissions set')
            return

        lj = max(len(p.name) for p in dct) + 2
        await ctx.print(FacadeText.join('\n', [
            f'{p.name.lower().ljust(lj)}: {ps.name.lower()}'
            for p, ps in dct.items()
        ]))
