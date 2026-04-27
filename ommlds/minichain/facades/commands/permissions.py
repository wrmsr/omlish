import typing as ta

from omlish import check
from omlish import lang
from omlish import marshal as msh
from omlish.argparse import all as ap
from omlish.formats import json
from omlish.formats import json5

from ...tools.permissions.managers import ToolPermissionsManager
from ...tools.permissions.types import ToolPermissionMatcher
from ...tools.permissions.types import ToolPermissionRule
from ...tools.permissions.types import ToolPermissionState
from ..text import FacadeText
from ..text import FacadeTextColor
from .base import ParserClassCommand


##


class PermissionsCommand(ParserClassCommand):
    def __init__(self, permissions: ToolPermissionsManager) -> None:
        super().__init__()

        self._permissions = permissions

    #

    _PERMISSION_STATE_COLORS: ta.ClassVar[ta.Mapping[ToolPermissionState, FacadeTextColor]] = {  # noqa
        ToolPermissionState.DENY: 'red',
        ToolPermissionState.ASK: 'yellow',
        ToolPermissionState.ALLOW: 'green',
    }

    @ap.cmd(
        name='list',
        default=True,
    )
    async def _run_list(self, ctx: ParserClassCommand.Context, args: ap.Namespace) -> None:
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

    @ap.cmd(
        ap.arg('state', choices=('allow', 'ask', 'deny')),
        ap.arg('kind'),
        ap.arg('body'),
        name='add',
    )
    async def _run_add(self, ctx: ParserClassCommand.Context, args: ap.Namespace) -> None:
        body = json5.loads(args.body or '{}', allow_ident_values=True)
        dct: dict = {check.non_empty_str(args.kind): body}
        matcher = msh.unmarshal(dct, ToolPermissionMatcher)
        rule = ToolPermissionRule(matcher, ToolPermissionState[args.state.upper()])

        self._permissions.add_rule(rule)
