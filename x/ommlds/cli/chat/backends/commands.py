from omcore import check
from omcore.argparse import all as ap

from .... import minichain as mc
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

    def _configure_parser(self, parser: ap.ArgumentParser) -> None:
        super()._configure_parser(parser)

        parser.add_argument('spec', nargs='?')

    async def _run_args(self, ctx: mc.facades.Command.Context, args: ap.Namespace) -> None:
        if (new_spec := args.spec) is not None:
            be = mc.BackendSpec.of(check.non_empty_str(new_spec))
            be = await self._manager.set_backend_spec(be)
        else:
            be = await self._manager.get_backend_spec()
        await ctx.print(be.as_json())
