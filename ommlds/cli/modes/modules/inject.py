from omlish import inject as inj
from omlish import lang

from .code.configs import CodeConfig
from .configs import ModuleConfig
from .skills.configs import SkillsConfig


with lang.auto_proxy_import(globals()):
    from .code import inject as _code
    from .skills import inject as _skills


##


def bind_module(cfg: ModuleConfig) -> inj.Elements:
    els: list[inj.Elemental] = []

    if isinstance(cfg, CodeConfig):
        els.extend(_code.bind_code(cfg))

    elif isinstance(cfg, SkillsConfig):
        els.extend(_skills.bind_skills(cfg))

    else:
        raise TypeError(cfg)

    return inj.as_elements(*els)
