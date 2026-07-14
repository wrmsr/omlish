from omlish import dataclasses as dc


##


@dc.dataclass(frozen=True, kw_only=True)
class OrmConfig:
    file_path: str | None = None
