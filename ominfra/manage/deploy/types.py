import typing as ta


DeployHome = ta.NewType('DeployHome', str)

DeployApp = ta.NewType('DeployApp', str)
DeployTag = ta.NewType('DeployTag', str)
DeployRev = ta.NewType('DeployRev', str)


class DeployAppTag(ta.NamedTuple):
    app: DeployApp
    tag: DeployTag