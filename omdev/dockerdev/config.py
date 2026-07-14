import typing as ta

from omcore import dataclasses as dc


##


DEFAULT_UID = 4317
DEFAULT_GID = DEFAULT_UID


@dc.dataclass(frozen=True)
class Config:
    base_image: str

    user: str | None = None
    uid: int = DEFAULT_UID
    gid: int = DEFAULT_GID

    workdir: str | None = None

    _: dc.KW_ONLY

    dep_sets: ta.Sequence[str] | None = None

    jdks: ta.Sequence[str] | None = None

    nvm_versions: ta.Sequence[str] | None = None

    rbenv_versions: ta.Sequence[str] | None = None

    uv_python_versions: ta.Sequence[str] | None = None

    pyenv_version_keys: ta.Sequence[str] | None = None

    cache_mounts: ta.Mapping[str, str] | None = None
