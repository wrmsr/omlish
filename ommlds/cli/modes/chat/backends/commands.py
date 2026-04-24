from omlish.argparse import all as ap

from ..... import minichain as mc
from ..backends.manager import BackendManager


##


class BackendCommand(mc.facades.Command):
    def __init__(
            self,
            *,
            manager: BackendManager,
    ) -> None:
        super().__init__()

        self._manager = manager

    async def _run_args(self, ctx: mc.facades.Command.Context, args: ap.Namespace) -> None:
        be = await self._manager.get_backend_spec()
        await ctx.print(be.as_json())
