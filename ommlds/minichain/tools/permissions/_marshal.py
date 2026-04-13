from omlish import lang
from omlish import marshal as msh

from .bash import BashToolPermissionMatcher  # noqa
from .fs import FsToolPermissionTarget  # noqa
from .fs import GlobFsToolPermissionMatcher  # noqa
from .types import ToolPermissionMatcher
from .types import ToolPermissionTarget
from .url import RegexUrlToolPermissionMatcher  # noqa
from .url import UrlToolPermissionTarget  # noqa


##


@lang.static_init
def _install_standard_marshaling() -> None:
    for cls in [
        ToolPermissionMatcher,
        ToolPermissionTarget,
    ]:
        msh.install_standard_factories(
            *msh.standard_polymorphism_factories(
                msh.polymorphism_from_subclasses(
                    cls,
                    strip_suffix=True,
                    naming=msh.Naming.SNAKE,
                ),
            ),
        )
