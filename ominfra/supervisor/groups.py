# ruff: noqa: UP006 UP007
import dataclasses as dc
import typing as ta

from .configs import ProcessConfig
from .configs import ProcessGroupConfig
from .context import ServerContext
from .dispatchers import Dispatcher
from .events import EventCallbacks
from .events import ProcessGroupAddedEvent
from .events import ProcessGroupRemovedEvent
from .states import ProcessState
from .types import AbstractProcessGroup
from .types import AbstractServerContext
from .types import AbstractSubprocess


##


@dc.dataclass(frozen=True)
class SubprocessFactory:
    fn: ta.Callable[[ProcessConfig, AbstractProcessGroup], AbstractSubprocess]

    def __call__(self, config: ProcessConfig, group: AbstractProcessGroup) -> AbstractSubprocess:
        return self.fn(config, group)


class ProcessGroup(AbstractProcessGroup):
    def __init__(
            self,
            config: ProcessGroupConfig,
            context: ServerContext,
            *,
            subprocess_factory: SubprocessFactory,
    ):
        super().__init__()

        self._config = config
        self._context = context
        self._subprocess_factory = subprocess_factory

        self._processes = {}
        for pconfig in self._config.processes or []:
            process = self._subprocess_factory(pconfig, self)
            self._processes[pconfig.name] = process

    @property
    def config(self) -> ProcessGroupConfig:
        return self._config

    @property
    def name(self) -> str:
        return self._config.name

    @property
    def context(self) -> AbstractServerContext:
        return self._context

    def __repr__(self):
        # repr can't return anything other than a native string, but the name might be unicode - a problem on Python 2.
        name = self._config.name
        return f'<{self.__class__.__name__} instance at {id(self)} named {name}>'

    def remove_logs(self) -> None:
        for process in self._processes.values():
            process.remove_logs()

    def reopen_logs(self) -> None:
        for process in self._processes.values():
            process.reopen_logs()

    def stop_all(self) -> None:
        processes = list(self._processes.values())
        processes.sort()
        processes.reverse()  # stop in desc priority order

        for proc in processes:
            state = proc.get_state()
            if state == ProcessState.RUNNING:
                # RUNNING -> STOPPING
                proc.stop()

            elif state == ProcessState.STARTING:
                # STARTING -> STOPPING
                proc.stop()

            elif state == ProcessState.BACKOFF:
                # BACKOFF -> FATAL
                proc.give_up()

    def get_unstopped_processes(self) -> ta.List[AbstractSubprocess]:
        return [x for x in self._processes.values() if not x.get_state().stopped]

    def get_dispatchers(self) -> ta.Dict[int, Dispatcher]:
        dispatchers: dict = {}
        for process in self._processes.values():
            dispatchers.update(process.get_dispatchers())
        return dispatchers

    def before_remove(self) -> None:
        pass

    def transition(self) -> None:
        for proc in self._processes.values():
            proc.transition()

    def after_setuid(self) -> None:
        for proc in self._processes.values():
            proc.create_auto_child_logs()


##


class ProcessGroups:
    def __init__(
            self,
            *,
            event_callbacks: EventCallbacks,
    ) -> None:
        super().__init__()

        self._event_callbacks = event_callbacks

        self._by_name: ta.Dict[str, ProcessGroup] = {}

    def get(self, name: str) -> ta.Optional[ProcessGroup]:
        return self._by_name.get(name)

    def __getitem__(self, name: str) -> ProcessGroup:
        return self._by_name[name]

    def __len__(self) -> int:
        return len(self._by_name)

    def __iter__(self) -> ta.Iterator[ProcessGroup]:
        return iter(self._by_name.values())

    def all(self) -> ta.Mapping[str, ProcessGroup]:
        return self._by_name

    def add(self, group: ProcessGroup) -> None:
        if (name := group.name) in self._by_name:
            raise KeyError(f'Process group already exists: {name}')

        self._by_name[name] = group

        self._event_callbacks.notify(ProcessGroupAddedEvent(name))

    def remove(self, name: str) -> None:
        group = self._by_name[name]

        group.before_remove()

        del self._by_name[name]

        self._event_callbacks.notify(ProcessGroupRemovedEvent(name))

    def clear(self) -> None:
        # FIXME: events?
        self._by_name.clear()
