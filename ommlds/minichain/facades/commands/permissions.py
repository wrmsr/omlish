import typing as ta

from omlish import check
from omlish import lang
from omlish import marshal as msh
from omlish.argparse import all as ap
from omlish.formats import json5
from omlish.formats.json import all as json

from ...tools.permissions.managers import ToolPermissionsManager
from ...tools.permissions.types import ToolPermissionMatcher
from ...tools.permissions.types import ToolPermissionRule
from ...tools.permissions.types import ToolPermissionState
from ...ui.text import CanUiText
from ...ui.text import UiText
from ...ui.text import UiTextColor
from .base import ParserClassCommand


##


class PermissionsCommand(ParserClassCommand):
    def __init__(self, permissions: ToolPermissionsManager) -> None:
        super().__init__()

        self._permissions = permissions

    #

    _PERMISSION_STATE_COLORS: ta.ClassVar[ta.Mapping[ToolPermissionState, UiTextColor]] = {  # noqa
        ToolPermissionState.DENY: 'red',
        ToolPermissionState.ASK: 'yellow',
        ToolPermissionState.ALLOW: 'green',
    }

    _TOOL_PERMISSION_STATE_NAME_LEN: ta.ClassVar = max(len(tps.name) for tps in ToolPermissionState)

    def _render_rule(self, rmd: str, r: ToolPermissionRule) -> CanUiText:
        sp = ' ' * 2
        return list(lang.interleave(sp, [
            rmd,
            UiText.style(
                r.result.name.lower().ljust(self._TOOL_PERMISSION_STATE_NAME_LEN),
                bold=True,
                color=self._PERMISSION_STATE_COLORS[r.result],
            ),
            json.dumps_compact(msh.marshal(r.matcher, ToolPermissionMatcher)),
        ]))

    def _render_rules(self, rs: ta.Iterable[tuple[str, ToolPermissionRule]]) -> CanUiText:
        return UiText.join('\n', [
            self._render_rule(rmd, r)
            for rmd, r in rs
        ])

    #

    @ap.cmd(
        name='list',
        default=True,
    )
    async def _run_list(self, ctx: ParserClassCommand.Context, args: ap.Namespace) -> None:
        rules = self._permissions.get_rules()
        if not rules:
            await ctx.print('No permissions set')
            return

        await ctx.print(self._render_rules(rules.by_min_digest.items()))

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

        rmd = self._permissions.get_rules().min_digests[rule]
        await ctx.print(self._render_rule(rmd, rule))
