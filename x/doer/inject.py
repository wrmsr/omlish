import dataclasses as dc
import typing as ta

from omlish.lite.inject import InjectorBindingOrBindings
from omlish.lite.inject import InjectorBindings
from omlish.lite.inject import inj

from .configs import DoerExecutableConfig
from .configs import PythonDoerDefConfig
from .configs import PythonDoerTaskConfig
from .configs import ShellDoerDefConfig
from .configs import ShellDoerTaskConfig
from .execution import DoerDefExecutor
from .execution import DoerExecutableExecutor
from .execution import DoerTaskExecutor
from .execution import PythonDoerDefExecutor
from .execution import PythonDoerTaskExecutor
from .execution import ShellDoerDefExecutor
from .execution import ShellDoerTaskExecutor


##


@dc.dataclass(frozen=True)
class DoerExecutableExecutorBinding:
    cfg_cls: ta.Type[DoerExecutableConfig]
    base_cls: ta.Type[DoerExecutableExecutor]
    impl_cls: ta.Type[DoerExecutableExecutor]


DoerExecutableExecutorBindingList = ta.NewType('DoerExecutableExecutorBindingList', ta.Sequence[DoerExecutableExecutorBinding])  # noqa


def bind_doer_executable_executor(
        cfg_cls: ta.Type[DoerExecutableConfig],
        base_cls: ta.Type[DoerExecutableExecutor],
        impl_cls: ta.Type[DoerExecutableExecutor],
) -> InjectorBindings:
    return inj.as_bindings(
        inj.bind(DoerExecutableExecutorBinding(cfg_cls, base_cls, impl_cls), array=True),
    )


##


def bind_doer() -> InjectorBindings:
    lst: ta.List[InjectorBindingOrBindings] = []

    lst.extend([
        inj.bind_array(DoerExecutableExecutorBinding),
        inj.bind_array_type(DoerExecutableExecutorBinding, DoerExecutableExecutorBindingList),

        bind_doer_executable_executor(ShellDoerTaskConfig, DoerTaskExecutor, ShellDoerTaskExecutor),
        bind_doer_executable_executor(PythonDoerTaskConfig, DoerTaskExecutor, PythonDoerTaskExecutor),
        bind_doer_executable_executor(ShellDoerDefConfig, DoerDefExecutor, ShellDoerDefExecutor),
        bind_doer_executable_executor(PythonDoerDefConfig, DoerDefExecutor, PythonDoerDefExecutor),
    ])

    return inj.as_bindings(*lst)
