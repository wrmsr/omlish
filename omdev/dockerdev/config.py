import typing as ta

from omlish import dataclasses as dc


##


@dc.dataclass(frozen=True)
class Config:
    base_image: str

    user: str | None = None
    uid: int = 2000
    gid: int = 2000

    workdir: str | None = None

    _: dc.KW_ONLY

    dep_sets: ta.Sequence[str] | None = None

    jdks: ta.Sequence[str] | None = None

    go_version: str | None = None

    zig_version: str | None = None

    nvm_versions: ta.Sequence[str] | None = None

    rbenv_versions: ta.Sequence[str] | None = None

    uv_python_versions: ta.Sequence[str] | None = None

    pyenv_version_keys: ta.Sequence[str] | None = None

    config_files: ta.Sequence[str] | None = None

    cache_mounts: ta.Mapping[str, str] | None = None
