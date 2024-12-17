import dataclasses as dc
import typing as ta

from omlish.lite.check import check


DeployPathKind = ta.Literal['dir', 'file']  # ta.TypeAlias
DeployPathPlaceholder = ta.Literal['app', 'tag', 'conf']  # ta.TypeAlias


##


DeployHome = ta.NewType('DeployHome', str)

DeployApp = ta.NewType('DeployApp', str)
DeployTag = ta.NewType('DeployTag', str)
DeployRev = ta.NewType('DeployRev', str)
DeployKey = ta.NewType('DeployKey', str)


##


@dc.dataclass(frozen=True)
class DeployAppTag:
    app: DeployApp
    tag: DeployTag

    def __post_init__(self) -> None:
        for s in [self.app, self.tag]:
            check.non_empty_str(s)
            check.equal(s, s.strip())

    def placeholders(self) -> ta.Mapping[DeployPathPlaceholder, str]:
        return {
            'app': self.app,
            'tag': self.tag,
        }
