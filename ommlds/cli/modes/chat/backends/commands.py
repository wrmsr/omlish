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

        ap.configure_parser_class_parser(type(self), parser)

    async def _run_args(self, ctx: mc.facades.Command.Context, args: ap.Namespace) -> None:
        cmd = getattr(args, '_cmd', None)

        # if self._unknown_args and not (cmd is not None and cmd.accepts_unknown):
        #     msg = f'unrecognized arguments: {" ".join(self._unknown_args)}'
        #     if (parser := self.get_parser()).exit_on_error:  # noqa
        #         parser.error(msg)
        #     else:
        #         raise argparse.ArgumentError(None, msg)

        if cmd is None:
            self._parser.print_help()
            return

        fn = cmd.__get__(self, type(self))

        await fn(ctx, args)

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
