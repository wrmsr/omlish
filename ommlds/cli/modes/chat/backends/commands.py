from omlish import check
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

    def _configure_parser(self, parser: ap.ArgumentParser) -> None:
        super()._configure_parser(parser)

        subparsers = parser.add_subparsers()
        parser.set_defaults(cmd='get')

        parser_list = subparsers.add_parser('get')
        parser_list.set_defaults(cmd='get')

        parser_set = subparsers.add_parser('set')
        parser_set.set_defaults(cmd='set')
        parser_set.add_argument('spec')

    async def _run_args(self, ctx: mc.facades.Command.Context, args: ap.Namespace) -> None:
        if args.cmd == 'get':
            await self._run_get(ctx, args)
        elif args.cmd == 'set':
            await self._run_set(ctx, args)
        else:
            raise RuntimeError(f'Unknown command: {args.cmd}')

    async def _run_get(self, ctx: mc.facades.Command.Context, args: ap.Namespace) -> None:
        be = await self._manager.get_backend_spec()
        await ctx.print(be.as_json())

    async def _run_set(self, ctx: mc.facades.Command.Context, args: ap.Namespace) -> None:
        be = mc.BackendSpec.of(check.non_empty_str(args.spec))
        be = await self._manager.set_backend_spec(be)
        await ctx.print(be.as_json())
