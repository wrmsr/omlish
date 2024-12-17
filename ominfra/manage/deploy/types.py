import typing as ta


DeployHome = ta.NewType('DeployHome', str)

DeployApp = ta.NewType('DeployApp', str)
DeployTag = ta.NewType('DeployTag', str)
DeployRev = ta.NewType('DeployRev', str)
DeployKey = ta.NewType('DeployKey', str)

DeployPathKind = ta.Literal['dir', 'file']  # ta.TypeAlias
DeployPathPlaceholder = ta.Literal['app', 'tag', 'conf']  # ta.TypeAlias


class DeployAppTag(ta.NamedTuple):
    app: DeployApp
    tag: DeployTag

    def placeholders(self) -> ta.Mapping[DeployPathPlaceholder, str]:
        return {
            'app': self.app,
            'tag': self.tag,
        }
