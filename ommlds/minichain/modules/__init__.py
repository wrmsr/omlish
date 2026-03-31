# fmt: off
# ruff: noqa: I001
from omlish import dataclasses as _dc  # noqa


_dc.init_package(
    globals(),
    codegen=True,
)


##


from omlish import lang as _lang  # noqa


with _lang.auto_proxy_init(globals()):
    ##

    from .bash.configs import BashConfig  # noqa
    from .code.configs import CodeConfig  # noqa
    from .fs.configs import FsConfig  # noqa
    from .skills.configs import SkillsConfig  # noqa
    from .todo.configs import TodoConfig  # noqa

    #

    from .configs import ModuleConfig  # noqa

    ##

    from . import inject  # noqa
