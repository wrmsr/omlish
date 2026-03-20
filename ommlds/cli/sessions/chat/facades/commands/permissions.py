import typing as ta

from omlish import lang
from omlish import marshal as msh
from omlish.argparse import all as argparse
from omlish.formats import json

from ...... import minichain as mc
from ...facades.text import FacadeText
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
        rules = self._permissions.get_rules()
        if not rules:
            await ctx.print('No permissions set')
            return

        sp = ' ' * 2
        slj = max(len(tps.name) for tps in mc.ToolPermissionState)
        await ctx.print(FacadeText.join('\n', [
            list(lang.interleave(sp, [
                rmd,
                FacadeText.style(
                    r.result.name.lower().ljust(slj),
                    bold=True,
                    color=self._PERMISSION_STATE_COLORS[r.result],
                ),
                json.dumps_compact(msh.marshal(r.matcher, mc.ToolPermissionMatcher)),
            ]))
            for rmd, r in rules.by_min_digest.items()
        ]))

    #

    async def _run_set(self, ctx: Command.Context, args: argparse.Namespace) -> None:
        # tp = self._permissions.get_tool_permissions()[args.name]
        # self._permissions.set_tool_permission_state(tp, mc.ToolPermissionState[args.state.upper()])
        raise NotImplementedError
