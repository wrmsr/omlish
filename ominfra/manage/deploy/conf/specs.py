# ruff: noqa: UP006 UP007
import abc
import dataclasses as dc
import typing as ta

from omlish.formats.ini.sections import IniSectionSettingsMap
from omlish.lite.check import check
from omlish.lite.marshal import register_single_field_type_obj_marshaler

from ..paths.specs import check_valid_deploy_spec_path


##


class DeployAppConfContent(abc.ABC):  # noqa
    pass


#


@register_single_field_type_obj_marshaler('body')
@dc.dataclass(frozen=True)
class RawDeployAppConfContent(DeployAppConfContent):
    body: str


#


@register_single_field_type_obj_marshaler('obj')
@dc.dataclass(frozen=True)
class JsonDeployAppConfContent(DeployAppConfContent):
    obj: ta.Any


#


@register_single_field_type_obj_marshaler('sections')
@dc.dataclass(frozen=True)
class IniDeployAppConfContent(DeployAppConfContent):
    sections: IniSectionSettingsMap


#


@register_single_field_type_obj_marshaler('items')
@dc.dataclass(frozen=True)
class NginxDeployAppConfContent(DeployAppConfContent):
    items: ta.Any


##


@dc.dataclass(frozen=True)
class DeployAppConfFile:
    path: str
    content: DeployAppConfContent

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
