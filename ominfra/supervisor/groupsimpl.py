# ruff: noqa: UP006 UP007 UP045
import typing as ta

from omlish.lite.check import check
from omlish.lite.typing import Func2

from .configs import ProcessConfig
from .configs import ProcessGroupConfig
from .states import ProcessState
from .types import Process
from .types import ProcessGroup


##


class ProcessFactory(Func2[ProcessConfig, ProcessGroup, Process]):
    pass


class ProcessGroupImpl(ProcessGroup):
    def __init__(
            self,
            config: ProcessGroupConfig,
            *,
            process_factory: ProcessFactory,
    ):
        super().__init__()

        self._config = config
        self._process_factory = process_factory

        by_name: ta.Dict[str, Process] = {}
        for pconfig in self._config.processes or []:
            p = check.isinstance(self._process_factory(pconfig, self), Process)
            if p.name in by_name:
                raise KeyError(f'name {p.name} of process {p} already registered by {by_name[p.name]}')
            by_name[pconfig.name] = p
        self._by_name = by_name

    @property
    def _by_key(self) -> ta.Mapping[str, Process]:
        return self._by_name

    #

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} instance at {id(self)} named {self._config.name}>'

    #

    @property
    def name(self) -> str:
        return self._config.name

    @property
    def config(self) -> ProcessGroupConfig:
        return self._config

    @property
    def by_name(self) -> ta.Mapping[str, Process]:
        return self._by_name

    #

    def get_unstopped_processes(self) -> ta.List[Process]:
        return [x for x in self if not x.state.stopped]

    def stop_all(self) -> None:
        processes = list(self._by_name.values())
        processes.sort()
        processes.reverse()  # stop in desc priority order

        for proc in processes:
            state = proc.state
            if state == ProcessState.RUNNING:
                # RUNNING -> STOPPING
                proc.stop()

            elif state == ProcessState.STARTING:
                # STARTING -> STOPPING
                proc.stop()

            elif state == ProcessState.BACKOFF:
                # BACKOFF -> FATAL
                proc.give_up()

    def before_remove(self) -> None:
        pass
