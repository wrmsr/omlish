from omlish import inject as inj
from omlish import lang

from ...drivers.tools.injection import tool_catalog_entries
from ...facades.commands.injection import commands
from .configs import SkillsConfig


with lang.auto_proxy_import(globals()):
    from . import commands as _commands
    from . import manager as _manager
    from . import tools as _tools


##


def bind_skills(cfg: SkillsConfig = SkillsConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.extend([
        inj.bind(cfg),
        inj.bind(_manager.SkillsManager, singleton=True),
    ])

    #

    for cmd_cls in [
        _commands.SkillsCommand,
        _commands.SkillCommand,
    ]:
        els.extend([
            inj.bind(cmd_cls, singleton=True),
            commands().bind_item(to_key=cmd_cls),
        ])

    #

    els.append(
        tool_catalog_entries().bind_item_consts(
            _tools.skill_tool(),
        ),
    )

    #

    return inj.as_elements(*els)
