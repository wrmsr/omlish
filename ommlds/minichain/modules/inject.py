from omlish import inject as inj
from omlish import lang

from .bash.configs import BashConfig
from .code.configs import CodeConfig
from .configs import ModuleConfig
from .fs.configs import FsConfig
from .skills.configs import SkillsConfig
from .todo.configs import TodoConfig


with lang.auto_proxy_import(globals()):
    from .bash import inject as _bash
    from .code import inject as _code
    from .fs import inject as _fs
    from .skills import inject as _skills
    from .todo import inject as _todo


##


def bind_module(cfg: ModuleConfig) -> inj.Elements:
    els: list[inj.Elemental] = []

    if isinstance(cfg, BashConfig):
        els.extend(_bash.bind_bash(cfg))

    elif isinstance(cfg, CodeConfig):
        els.extend(_code.bind_code(cfg))

    elif isinstance(cfg, FsConfig):
        els.extend(_fs.bind_fs(cfg))

    elif isinstance(cfg, SkillsConfig):
        els.extend(_skills.bind_skills(cfg))

    elif isinstance(cfg, TodoConfig):
        els.extend(_todo.bind_todo(cfg))

    else:
        raise TypeError(cfg)

    return inj.as_elements(*els)
