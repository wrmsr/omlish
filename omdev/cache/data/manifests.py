import datetime

from omlish import __about__ as about
from omlish import cached
from omlish import dataclasses as dc

from ...git.revisions import get_git_revision
from .consts import SERIALIZATION_VERSION
from .specs import Spec


##


@cached.function
def _lib_revision() -> str | None:
    if (rev := about.__revision__) is not None:
        return rev  # type: ignore

    return get_git_revision()


##


@dc.dataclass(frozen=True)
class Manifest:
    spec: Spec

    start_at: datetime.datetime = dc.field(kw_only=True)
    end_at: datetime.datetime = dc.field(kw_only=True)

    lib_version: str = dc.field(default_factory=lambda: about.__version__, kw_only=True)
    lib_revision: str = dc.field(default_factory=_lib_revision, kw_only=True)

    serialization_version: int = dc.field(default=SERIALIZATION_VERSION, kw_only=True)

    @dc.validate
    def _validate_serialization_versions(self) -> bool:
        return self.serialization_version == self.spec.serialization_version
