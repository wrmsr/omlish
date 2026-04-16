import typing as ta

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


CONFIG_MODULES: ta.Mapping[type[ModuleConfig], ta.Callable[[ta.Any], inj.Elements]] = {
    BashConfig: lambda cfg: _bash.bind_bash(cfg),
    CodeConfig: lambda cfg: _code.bind_code(cfg),
    FsConfig: lambda cfg: _fs.bind_fs(cfg),
    SkillsConfig: lambda cfg: _skills.bind_skills(cfg),
    TodoConfig: lambda cfg: _todo.bind_todo(cfg),
}


def bind_module(cfg: ModuleConfig) -> inj.Elements:
    els: list[inj.Elemental] = []

    for cls, bind_fn in CONFIG_MODULES.items():
        if isinstance(cfg, cls):
            els.extend(bind_fn(cfg))
            break
    else:
        raise TypeError(cfg)

    return inj.as_elements(*els)
