import io

from omlish.argparse import all as argparse

from ...drivers.permissions import Permissions
from .base import Command


##


class PermissionsCommand(Command):
    def __init__(self, permissions: Permissions) -> None:
        super().__init__()

        self._permissions = permissions

    async def _run_args(self, ctx: Command.Context, args: argparse.Namespace) -> None:
        out = io.StringIO()
        for i, (p, ps) in enumerate(self._permissions.get_permission_states().items()):
            if i:
                out.write('\n')
            out.write(f'{p.name.lower()}: {ps.name.lower()}')
        await ctx.print(out.getvalue())
