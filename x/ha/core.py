"""
- Dashboards
- Integrations
- Devices
 - Entities
- Automations
 - Triggers
 - Conditions
 - Actions
- Scripts
- Scenes

--

- Event Bus
- State Machine
- Service Registry
- Timer

"""
import asyncio
import datetime
import enum
import itertools
import typing as ta

from omlish import dataclasses as dc


@dc.dataclass(frozen=True)
class EventContext:
    user_id: str | None = None


class EventOrigin(enum.Enum):
    LOCAL = enum.auto()
    REMOTE = enum.auto()


@dc.dataclass(frozen=True)
class Event:
    event_type: str
    data: ta.Any = None
    origin: EventOrigin | None = None
    at: datetime.datetime | None = None
    context: EventContext | None = None


P = ta.ParamSpec('P')
R = ta.TypeVar('R')
R_co = ta.TypeVar('R_co', covariant=True)


@dc.dataclass(frozen=True)
class Job(ta.Generic[P, R_co]):
    target: ta.Callable[P, R_co]
    name: str | None = None
    cancel_on_shutdown: bool | None = None


class JobRunner:
    def schedule_job(
            self,
            job: Job[..., ta.Coroutine[ta.Any, ta.Any, R] | R],
            *args: ta.Any,
            **kwargs: ta.Any,
    ) -> asyncio.Future[R] | None:
        # FIXME
        pass


class EventBus:
    @dc.dataclass(frozen=True)
    class Listener:
        job: Job[[Event], ta.Coroutine[ta.Any, ta.Any, None]] | None = None
        filter: ta.Callable[[Event], bool] | None = None
        run_immediately: bool = False

    def __init__(self, job_runner: JobRunner) -> None:
        super().__init__()

        self._job_runner = job_runner

        self._listeners: dict[str | None, list['EventBus.Listener']] = {}

    def fire(self, event: Event) -> None:
        for l in itertools.chain(
            self._listeners.get(event.event_type, ()),
            self._listeners.get(None, ()),
        ):
            if l.filter is not None:
                try:
                    if not l.filter(event):
                        continue
                except Exception:  # noqa
                    # FIXME: log
                    continue

            if l.run_immediately:
                try:
                    l.job.target(event)
                except Exception:  # noqa
                    # FIXME: log
                    pass

            else:
                self._job_runner.schedule_job(l.job, event)
