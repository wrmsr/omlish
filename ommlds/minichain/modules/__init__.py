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

    from .code.configs import CodeConfig  # noqa

    from .skills.configs import SkillsConfig  # noqa

    from .configs import ModuleConfig  # noqa

    ##

    from . import inject  # noqa
