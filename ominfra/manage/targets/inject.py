# ruff: noqa: UP006 UP007 UP045
import typing as ta

from omcore.lite.inject import Injector
from omcore.lite.inject import InjectorBindingOrBindings
from omcore.lite.inject import InjectorBindings
from omcore.lite.inject import inj

from .connection import DockerManageTargetConnector
from .connection import LocalManageTargetConnector
from .connection import ManageTargetConnector
from .connection import ManageTargetConnectorMap
from .connection import SshManageTargetConnector
from .connection import TypeSwitchedManageTargetConnector
from .targets import DockerManageTarget
from .targets import LocalManageTarget
from .targets import SshManageTarget


##


def bind_targets() -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = [
        inj.bind(LocalManageTargetConnector, singleton=True),
        inj.bind(DockerManageTargetConnector, singleton=True),
        inj.bind(SshManageTargetConnector, singleton=True),

        inj.bind(TypeSwitchedManageTargetConnector, singleton=True),
        inj.bind(ManageTargetConnector, to_key=TypeSwitchedManageTargetConnector),
    ]

    #

    def provide_manage_target_connector_map(injector: Injector) -> ManageTargetConnectorMap:
        return ManageTargetConnectorMap({
            LocalManageTarget: injector[LocalManageTargetConnector],
            DockerManageTarget: injector[DockerManageTargetConnector],
            SshManageTarget: injector[SshManageTargetConnector],
        })
    lst.append(inj.bind(provide_manage_target_connector_map, singleton=True))

    #

    return inj.as_bindings(*lst)
