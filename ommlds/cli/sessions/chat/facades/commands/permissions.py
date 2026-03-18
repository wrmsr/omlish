import typing as ta

from omlish.argparse import all as argparse

from ...... import minichain as mc
from ...facades.text import FacadeTextColor
from .base import Command


##


class PermissionsCommand(Command):
    def __init__(self, permissions: 'mc.ToolPermissionsManager') -> None:
        super().__init__()

        self._permissions = permissions

    def _configure_parser(self, parser: argparse.ArgumentParser) -> None:
        super()._configure_parser(parser)

        subparsers = parser.add_subparsers()
        parser.set_defaults(cmd='list')

        parser_list = subparsers.add_parser('list')
        parser_list.set_defaults(cmd='list')

        parser_set = subparsers.add_parser('set')
        parser_set.add_argument('name')
        parser_set.add_argument('state', choices=('allow', 'ask', 'deny'))
        parser_set.set_defaults(cmd='set')

    async def _run_args(self, ctx: Command.Context, args: argparse.Namespace) -> None:
        if args.cmd == 'list':
            await self._run_list(ctx, args)
        elif args.cmd == 'set':
            await self._run_set(ctx, args)
        else:
            raise RuntimeError(f'Unknown command: {args.cmd}')

    #

    _PERMISSION_STATE_COLORS: ta.ClassVar[ta.Mapping['mc.ToolPermissionState', FacadeTextColor]] = {  # noqa
        mc.ToolPermissionState.DENY: 'red',
        mc.ToolPermissionState.ASK: 'yellow',
        mc.ToolPermissionState.ALLOW: 'green',
    }

    async def _run_list(self, ctx: Command.Context, args: argparse.Namespace) -> None:
        lst = self._permissions.get_rules()
        if not lst:
            await ctx.print('No permissions set')
            return

        # lj = max(len(p.name) for p in dct) + 2
        # await ctx.print(FacadeText.join('\n', [
        #     [
        #         f'{p.name.lower().ljust(lj)}: ',
        #         FacadeText.style(
        #             ps.name.lower(),
        #             bold=True,
        #             color=self._PERMISSION_STATE_COLORS[ps],
        #         ),
        #     ]
        #     for p, ps in dct.items()
        # ]))

        for r in lst:
            await ctx.print(repr(r))

    #

    async def _run_set(self, ctx: Command.Context, args: argparse.Namespace) -> None:
        # tp = self._permissions.get_tool_permissions()[args.name]
        # self._permissions.set_tool_permission_state(tp, mc.ToolPermissionState[args.state.upper()])
        raise NotImplementedError
