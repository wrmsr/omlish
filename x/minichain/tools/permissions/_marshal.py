from omcore import marshal as msh

from .bash import BashToolPermissionMatcher  # noqa
from .fs import FsToolPermissionTarget  # noqa
from .fs import GlobFsToolPermissionMatcher  # noqa
from .types import ToolPermissionMatcher
from .types import ToolPermissionTarget
from .url import RegexUrlToolPermissionMatcher  # noqa
from .url import UrlToolPermissionTarget  # noqa


##


@msh.register_global_lazy_init
def _install_standard_marshaling(cfgs: msh.ConfigRegistry) -> None:
    for cls in [
        ToolPermissionMatcher,
        ToolPermissionTarget,
    ]:
        msh.install_standard_factories(
            cfgs,
            *msh.standard_polymorphism_factories(
                msh.polymorphism_from_subclasses(
                    cls,
                    strip_suffix=True,
                    naming=msh.Naming.SNAKE,
                ),
            ),
        )
