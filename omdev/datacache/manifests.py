import datetime

from omlish import __about__ as about
from omlish import cached
from omlish import dataclasses as dc

from ..revisions import get_git_revision
from .consts import MARSHAL_VERSION
from .specs import CacheDataSpec


##


@cached.function
def _lib_revision() -> str | None:
    if (rev := about.__revision__) is not None:
        return rev  # type: ignore

    return get_git_revision()


##


@dc.dataclass(frozen=True)
class CacheDataManifest:
    spec: CacheDataSpec

    start_at: datetime.datetime = dc.field(kw_only=True)
    end_at: datetime.datetime = dc.field(kw_only=True)

    lib_version: str = dc.field(default_factory=lambda: about.__version__, kw_only=True)
    lib_revision: str = dc.field(default_factory=_lib_revision, kw_only=True)

    marshal_version: int = dc.field(default=MARSHAL_VERSION, kw_only=True)

    @dc.validate
    def _validate_marshal_versions(self) -> bool:
        return self.marshal_version == self.spec.marshal_version
