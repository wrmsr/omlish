import typing as ta

from ... import minichain as mc


ServiceT = ta.TypeVar('ServiceT', bound=mc.Service)


##


BackendName = ta.NewType('BackendName', str)
DefaultBackendName = ta.NewType('DefaultBackendName', str)

BackendConfigs = ta.NewType('BackendConfigs', ta.Sequence['mc.Config'])
