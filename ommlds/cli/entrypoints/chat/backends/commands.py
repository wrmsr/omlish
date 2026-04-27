from omlish import check
from omlish.argparse import all as ap

from ..... import minichain as mc
from ..backends.manager import BackendManager


##


class BackendCommand(mc.facades.ParserClassCommand):
    def __init__(
            self,
            *,
            manager: BackendManager,
    ) -> None:
        super().__init__()

        self._manager = manager

    @ap.cmd(
        name='get',
        default=True,
    )
    async def _run_get(self, ctx: mc.facades.Command.Context, args: ap.Namespace) -> None:
        be = await self._manager.get_backend_spec()
        await ctx.print(be.as_json())

    @ap.cmd(
        ap.arg('spec'),
        name='set',
    )
    async def _run_set(self, ctx: mc.facades.Command.Context, args: ap.Namespace) -> None:
        be = mc.BackendSpec.of(check.non_empty_str(args.spec))
        be = await self._manager.set_backend_spec(be)
        await ctx.print(be.as_json())
