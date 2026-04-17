import typing as ta

from omlish import check
from omlish import lang
from omlish import marshal as msh
from omlish.argparse import all as argparse
from omlish.formats import json
from omlish.formats import json5

from ...tools.permissions.managers import ToolPermissionsManager
from ...tools.permissions.types import ToolPermissionMatcher
from ...tools.permissions.types import ToolPermissionRule
from ...tools.permissions.types import ToolPermissionState
from ..text import FacadeText
from ..text import FacadeTextColor
from .base import Command


##


class PermissionsCommand(Command):
    def __init__(self, permissions: ToolPermissionsManager) -> None:
        super().__init__()

        self._permissions = permissions

    def _configure_parser(self, parser: argparse.ArgumentParser) -> None:
        super()._configure_parser(parser)

        subparsers = parser.add_subparsers()
        parser.set_defaults(cmd='list')

        parser_list = subparsers.add_parser('list')
        parser_list.set_defaults(cmd='list')

        parser_set = subparsers.add_parser('add')
        parser_set.add_argument('state', choices=('allow', 'ask', 'deny'))
        parser_set.add_argument('kind')
        parser_set.add_argument('body')
        parser_set.set_defaults(cmd='add')

    async def _run_args(self, ctx: Command.Context, args: argparse.Namespace) -> None:
        if args.cmd == 'list':
            await self._run_list(ctx, args)
        elif args.cmd == 'add':
            await self._run_add(ctx, args)
        else:
            raise RuntimeError(f'Unknown command: {args.cmd}')

    #

    _PERMISSION_STATE_COLORS: ta.ClassVar[ta.Mapping[ToolPermissionState, FacadeTextColor]] = {  # noqa
        ToolPermissionState.DENY: 'red',
        ToolPermissionState.ASK: 'yellow',
        ToolPermissionState.ALLOW: 'green',
    }

    async def _run_list(self, ctx: Command.Context, args: argparse.Namespace) -> None:
        rules = self._permissions.get_rules()
        if not rules:
            await ctx.print('No permissions set')
            return

        sp = ' ' * 2
        slj = max(len(tps.name) for tps in ToolPermissionState)
        await ctx.print(FacadeText.join('\n', [
            list(lang.interleave(sp, [
                rmd,
                FacadeText.style(
                    r.result.name.lower().ljust(slj),
                    bold=True,
                    color=self._PERMISSION_STATE_COLORS[r.result],
                ),
                json.dumps_compact(msh.marshal(r.matcher, ToolPermissionMatcher)),
            ]))
            for rmd, r in rules.by_min_digest.items()
        ]))

    #

    async def _run_add(self, ctx: Command.Context, args: argparse.Namespace) -> None:
        dct: dict = {check.non_empty_str(args.kind): json5.loads(args.body or '{}')}
        matcher = msh.unmarshal(dct, ToolPermissionMatcher)
        rule = ToolPermissionRule(matcher, ToolPermissionState[args.state.upper()])

        self._permissions.add_rule(rule)
