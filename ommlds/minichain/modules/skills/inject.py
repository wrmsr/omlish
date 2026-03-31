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
        inj.bind(_manager.SkillsManager, singleton=True),
    ])

    #

    els.extend([
        inj.bind(_commands.SkillCommand, singleton=True),
        commands().bind_item(to_key=_commands.SkillCommand),
    ])

    #

    els.append(
        tool_catalog_entries().bind_item_consts(
            _tools.skill_tool(),
        ),
    )

    #

    return inj.as_elements(*els)
