# ruff: noqa: UP006 UP007
import dataclasses as dc
import typing as ta

from omlish.lite.check import check

from ..paths.specs import check_valid_deploy_spec_path


##


@dc.dataclass(frozen=True)
class DeployAppConfFile:
    path: str
    body: str

    def __post_init__(self) -> None:
        check_valid_deploy_spec_path(self.path)


##


@dc.dataclass(frozen=True)
class DeployAppConfLink:  # noqa
    """
    May be either:
     - @conf(.ext)* - links a single file in root of app conf dir to conf/@conf/@dst(.ext)*
     - @conf/file - links a single file in a single subdir to conf/@conf/@dst--file
     - @conf/ - links a directory in root of app conf dir to conf/@conf/@dst/
    """

    src: str

    kind: ta.Literal['current_only', 'all_active'] = 'current_only'

    def __post_init__(self) -> None:
        check_valid_deploy_spec_path(self.src)
        if '/' in self.src:
            check.equal(self.src.count('/'), 1)


##


@dc.dataclass(frozen=True)
class DeployAppConfSpec:
    files: ta.Optional[ta.Sequence[DeployAppConfFile]] = None

    links: ta.Optional[ta.Sequence[DeployAppConfLink]] = None

    def __post_init__(self) -> None:
        if self.files:
            seen: ta.Set[str] = set()
            for f in self.files:
                check.not_in(f.path, seen)
                seen.add(f.path)
