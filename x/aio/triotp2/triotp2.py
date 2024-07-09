import abc
import collections
import contextlib
import contextvars
import dataclasses as dc
import enum
import logging
import typing as ta
import uuid

import tenacity
import trio

from omlish import lang
from .. import trio_util


# mailbox


MailboxID = ta.TypeVar('MailboxID', bound=str)  # Mailbox identifier (UUID4)


class MailboxDoesNotExist(RuntimeError):
    def __init__(self, mid: MailboxID) -> None:
        super().__init__(f'mailbox {mid} does not exist')


class NameAlreadyExist(RuntimeError):
    def __init__(self, name: str) -> None:
        super().__init__(f'mailbox {name} already registered')


class NameDoesNotExist(RuntimeError):
    def __init__(self, name: str) -> None:
        super().__init__(f'mailbox {name} does not exist')


class Mailboxes:
    def __init__(self):
        super().__init__()
        self.mailboxes = {}
        self.names = {}

    def create(self) -> MailboxID:
        mid = str(uuid.uuid4())

        self.mailboxes[mid] = trio.open_memory_channel(0)

        return mid

    async def destroy(self, mid: MailboxID) -> None:
        if mid not in self.mailboxes:
            raise MailboxDoesNotExist(mid)

        self.unregister_all(mid)

        wchan, rchan = self.mailboxes.pop(mid)
        await wchan.aclose()
        await rchan.aclose()

    def register(self, mid: MailboxID, name: str) -> None:
        if mid not in self.mailboxes:
            raise MailboxDoesNotExist(mid)

        if name in self.names:
            raise NameAlreadyExist(name)

        self.names[name] = mid

    def unregister(self, name: str) -> None:
        if name not in self.names:
            raise NameDoesNotExist(name)

        self.names.pop(name)

    def unregister_all(self, mid: MailboxID) -> None:
        for name, mailbox_id in list(self.names.items()):
            if mailbox_id == mid:
                self.names.pop(name)

    @contextlib.asynccontextmanager
    async def open(self, name: str | None = None) -> ta.AsyncContextManager[MailboxID]:
        mid = self.create()

        try:
            if name is not None:
                self.register(mid, name)

            yield mid

        finally:
            await self.destroy(mid)

    def _resolve(self, name: str) -> MailboxID | None:
        return self.names.get(name)

    async def send(self, name_or_mid: str | MailboxID, message: ta.Any) -> None:
        mid = self._resolve(name_or_mid)
        if mid is None:
            mid = name_or_mid

        if mid not in self.mailboxes:
            raise MailboxDoesNotExist(mid)

        wchan, _ = self.mailboxes.get(mid)
        await wchan.send(message)

    async def receive(
            self,
            mid: MailboxID,
            timeout: float | None = None,
            on_timeout: ta.Callable[[], ta.Awaitable[ta.Any]] = None,
    ) -> ta.Any:
        if mid not in self.mailboxes:
            raise MailboxDoesNotExist(mid)

        _, rchan = self.mailboxes.get(mid)

        if timeout is not None:
            try:
                with trio.fail_after(timeout):
                    return await rchan.receive()

            except trio.TooSlowError:
                if on_timeout is None:
                    raise

                return await on_timeout()

        else:
            return await rchan.receive()


_context_mailboxes = contextvars.ContextVar('mailboxes')


def init_mailboxes() -> None:
    _context_mailboxes.set(Mailboxes())


def mailboxes() -> 'Mailboxes':
    return _context_mailboxes.get()


# supervisor


class RestartStrategy(enum.Enum):
    PERMANENT = enum.auto()  # Always restart the task
    TRANSIENT = enum.auto()  # Restart the task only if it raises an exception
    TEMPORARY = enum.auto()  # Never restart a task


class _RetryStrategy:
    def __init__(
            self,
            restart: RestartStrategy,
            max_restarts: int,
            max_seconds: float,
    ) -> None:
        super().__init__()
        self.restart = restart
        self.max_restarts = max_restarts
        self.max_seconds = max_seconds

        self.failure_times = collections.deque()

    def __call__(self, retry_state: tenacity.RetryCallState) -> bool:
        match self.restart:
            case RestartStrategy.PERMANENT:
                pass

            case RestartStrategy.TRANSIENT:
                if not retry_state.outcome.failed:
                    return False

            case RestartStrategy.TEMPORARY:
                return False

        now = trio.current_time()
        self.failure_times.append(now)

        if len(self.failure_times) <= self.max_restarts:
            return True

        oldest_failure = self.failure_times.popleft()
        return now - oldest_failure >= self.max_seconds


class _RetryLogger:
    logger = logging.getLogger(f'{__name__}._RetryLogger')

    def __init__(self, child_id: str) -> None:
        super().__init__()
        self.child_id = child_id

    def __call__(self, retry_state: tenacity.RetryCallState) -> None:
        if isinstance(retry_state.outcome.exception(), trio.Cancelled):
            self.logger.info('task cancelled', extra=dict(child_id=self.child_id))

        elif retry_state.outcome.failed:
            exception = retry_state.outcome.exception()
            exc_info = (exception.__class__, exception, exception.__traceback__)
            self.logger.error('restarting task after failure', extra=dict(child_id=self.child_id), exc_info=exc_info)

        else:
            self.logger.error('restarting task after unexpected exit', extra=dict(child_id=self.child_id))


@dc.dataclass()
class ChildSpec:
    id: str  # Task identifier
    task: ta.Callable[..., ta.Awaitable[None]]  # The task to run
    args: list[ta.Any]  # Arguments to pass to the task
    restart: RestartStrategy = RestartStrategy.PERMANENT  # When to restart the task


@dc.dataclass()
class SupervisorOptions:
    max_restarts: int = 3  # Maximum number of restart during a limited timespan
    max_seconds: int = 5  # Timespan duration


class supervisor(lang.Namespace):  # noqa
    @classmethod
    async def start(
            cls,
            child_specs: list[ChildSpec],
            opts: SupervisorOptions,
            task_status=trio.TASK_STATUS_IGNORED,
    ) -> None:
        async with trio.open_nursery() as nursery:
            for spec in child_specs:
                await nursery.start(cls._child_monitor, spec, opts)

            task_status.started(None)

    @classmethod
    async def _child_monitor(
            cls,
            spec: ChildSpec,
            opts: SupervisorOptions,
            task_status=trio.TASK_STATUS_IGNORED,
    ) -> None:
        task_status.started(None)

        @tenacity.retry(
            retry=_RetryStrategy(spec.restart, opts.max_restarts, opts.max_seconds),
            reraise=True,
            sleep=trio.sleep,
            after=_RetryLogger(spec.id),
        )
        async def _child_runner():
            with trio_util.defer_to_cancelled():
                async with trio.open_nursery() as nursery:
                    nursery.start_soon(spec.task, *spec.args)

        await _child_runner()


# dynamic_supervisor


class dynamic_supervisor(lang.Namespace):  # noqa
    @classmethod
    async def start(
            cls,
            opts: SupervisorOptions,
            name: str | None = None,
            task_status=trio.TASK_STATUS_IGNORED,
    ) -> None:
        async with mailboxes().open(name) as mid:
            task_status.started(mid)

            async with trio.open_nursery() as nursery:
                await nursery.start(cls._child_listener, mid, opts, nursery)

    @classmethod
    async def start_child(
            cls,
            name_or_mid: str | MailboxID,
            child_spec: ChildSpec,
    ) -> None:
        await mailboxes().send(name_or_mid, child_spec)

    @classmethod
    async def _child_listener(
            cls,
            mid: MailboxID,
            opts: SupervisorOptions,
            nursery: trio.Nursery,
            task_status=trio.TASK_STATUS_IGNORED,
    ) -> None:
        task_status.started(None)

        while True:
            request = await mailboxes().receive(mid)

            match request:
                case ChildSpec() as spec:
                    await nursery.start(supervisor._child_monitor, spec, opts)  # noqa

                case _:
                    pass


# apps


class App(lang.Abstract):
    __name__: ta.ClassVar[str]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, '__name__'):
            raise TypeError

    @abc.abstractmethod
    async def start(self, start_arg: ta.Any) -> None:
        raise NotImplementedError


@dc.dataclass()
class AppSpec:
    app: App  # App app
    start_arg: ta.Any  # Argument to pass to the app's start function
    permanent: bool = True  # If `False`, the app won't be restarted if it exits
    opts: SupervisorOptions | None = None  # Options for the supervisor managing the app task


class Apps:
    def __init__(self, nursery: trio.Nursery) -> None:
        super().__init__()
        self.nursery = nursery
        self.registry = {}

    async def start(self, spec: AppSpec) -> None:
        if spec.app.__name__ not in self.registry:
            local_nursery = await self.nursery.start(self._scope, spec)
            self.registry[spec.app.__name__] = local_nursery

    async def stop(self, app_name: str) -> None:
        if app_name in self.registry:
            local_nursery = self.registry.pop(app_name)
            local_nursery.cancel_scope.cancel()

    @classmethod
    async def _scope(cls, spec: AppSpec, task_status=trio.TASK_STATUS_IGNORED) -> None:
        if spec.permanent:
            restart = RestartStrategy.PERMANENT
        else:
            restart = RestartStrategy.TRANSIENT

        async with trio.open_nursery() as nursery:
            task_status.started(nursery)

            children = [
                ChildSpec(
                    id=spec.app.__name__,
                    task=spec.app.start,
                    args=[spec.start_arg],
                    restart=restart,
                )
            ]
            opts = spec.opts if spec.opts is not None else SupervisorOptions()

            nursery.start_soon(supervisor.start, children, opts)


_context_apps = contextvars.ContextVar('apps')


def init_apps(nursery: trio.Nursery) -> None:
    _context_apps.set(Apps(nursery))


def apps() -> Apps:
    return _context_apps.get()


# node


class node(lang.Namespace):  # noqa
    @classmethod
    def run(cls, specs: list[AppSpec]) -> None:
        trio.run(cls._start, specs)

    @classmethod
    async def _start(cls, specs: list[AppSpec]) -> None:
        init_mailboxes()

        async with trio.open_nursery() as nursery:
            init_apps(nursery)

            for app_spec in specs:
                await apps().start(app_spec)


# gen_server


State = ta.TypeVar('State')


class GenServerExited(Exception):
    pass


@dc.dataclass()
class _Loop:
    yes: bool


@dc.dataclass()
class _Raise:
    exc: BaseException


Continuation = _Loop | _Raise


@dc.dataclass()
class Reply:
    payload: ta.Any  # The response to send back


@dc.dataclass()
class NoReply:
    pass


@dc.dataclass()
class Stop:
    reason: BaseException | None = None  # Eventual exception that caused the gen_server to stop


Caller: ta.TypeAlias = trio.MemorySendChannel


@dc.dataclass()
class _CallMessage:
    source: Caller
    payload: ta.Any


@dc.dataclass()
class _CastMessage:
    payload: ta.Any


class ServerApp(App, lang.Abstract):
    @abc.abstractmethod
    async def init(self, init_arg: ta.Any) -> State:
        raise NotImplementedError

    async def terminate(self, reason: BaseException | None, state: State) -> None:
        if reason is not None:
            logger = logging.getLogger(self.__name__)
            logger.exception(reason)

    async def handle_call(self, message, caller: Caller, state: State) -> tuple[Reply | NoReply | Stop, State]:
        raise TypeError(f'{self.__name__}.handle_call not implemented')

    async def handle_cast(self, message, state: State) -> tuple[NoReply | Stop, State]:
        raise TypeError(f'{self.__name__}.handle_cast not implemented')

    async def handle_info(self, message, state: State) -> tuple[NoReply | Stop, State]:
        return NoReply(), state


class gen_server(lang.Namespace):  # noqa
    @classmethod
    async def start(
            cls,
            app: ServerApp,
            init_arg: ta.Any | None = None,
            name: str | None = None,
    ) -> None:
        await _GenServerLoop(app).loop(init_arg, name)

    @classmethod
    async def call(
            cls,
            name_or_mid: str | MailboxID,
            payload: ta.Any,
            timeout: float | None = None,
    ) -> ta.Any:
        wchan, rchan = trio.open_memory_channel(0)
        message = _CallMessage(source=wchan, payload=payload)

        await mailboxes().send(name_or_mid, message)

        try:
            if timeout is not None:
                with trio.fail_after(timeout):
                    val = await rchan.receive()

            else:
                val = await rchan.receive()

            if isinstance(val, Exception):
                raise val

            return val

        finally:
            await wchan.aclose()
            await rchan.aclose()

    @classmethod
    async def cast(
            cls,
            name_or_mid: str | MailboxID,
            payload: ta.Any,
    ) -> None:
        message = _CastMessage(payload=payload)
        await mailboxes().send(name_or_mid, message)

    @classmethod
    async def reply(cls, caller: Caller, response: ta.Any) -> None:
        await caller.send(response)


class _GenServerLoop:
    def __init__(self, app: ServerApp) -> None:
        super().__init__()
        self.app = app

    async def loop(
            self,
            init_arg: ta.Any | None,
            name: str | None,
    ) -> None:
        async with mailboxes().open(name) as mid:
            try:
                state = await self._init(init_arg)
                looping = True

                while looping:
                    message = await mailboxes().receive(mid)

                    match message:
                        case _CallMessage(source, payload):
                            continuation, state = await self._handle_call(payload, source, state)
                        case _CastMessage(payload):
                            continuation, state = await self._handle_cast(payload, state)
                        case _:
                            continuation, state = await self._handle_info(message, state)

                    match continuation:
                        case _Loop(yes=False):
                            looping = False
                        case _Loop(yes=True):
                            looping = True
                        case _Raise(exc=err):
                            raise err

            except Exception as err:
                await self._terminate(err, state)
                raise err from None

            else:
                await self._terminate(None, state)

    async def _init(self, init_arg: ta.Any) -> State:
        return await self.app.init(init_arg)

    async def _terminate(
            self,
            reason: BaseException | None,
            state: State,
    ) -> None:
        await self.app.terminate(reason, state)

    async def _handle_call(
            self,
            message: ta.Any,
            source: trio.MemorySendChannel,
            state: State,
    ) -> tuple[Continuation, State]:
        result = await self.app.handle_call(message, source, state)

        match result:
            case (Reply(payload), new_state):
                state = new_state
                await gen_server.reply(source, payload)
                continuation = _Loop(yes=True)

            case (NoReply(), new_state):
                state = new_state
                continuation = _Loop(yes=True)

            case (Stop(reason), new_state):
                state = new_state
                await gen_server.reply(source, GenServerExited())

                if reason is not None:
                    continuation = _Raise(reason)
                else:
                    continuation = _Loop(yes=False)

            case _:
                raise TypeError(f'{self.app.__name__}.handle_call did not return a valid value')

        return continuation, state

    async def _handle_cast(
            self,
            message: ta.Any,
            state: State,
    ) -> tuple[Continuation, State]:
        result = await self.app.handle_cast(message, state)

        match result:
            case (NoReply(), new_state):
                state = new_state
                continuation = _Loop(yes=True)

            case (Stop(reason), new_state):
                state = new_state

                if reason is not None:
                    continuation = _Raise(reason)
                else:
                    continuation = _Loop(yes=False)

            case _:
                raise TypeError(f'{self.app.__name__}.handle_cast did not return a valid value')

        return continuation, state

    async def _handle_info(
            self,
            message: ta.Any,
            state: State,
    ) -> tuple[Continuation, State]:
        result = await self.app.handle_info(message, state)

        match result:
            case (NoReply(), new_state):
                state = new_state
                continuation = _Loop(yes=True)

            case (Stop(reason), new_state):
                state = new_state

                if reason is not None:
                    continuation = _Raise(reason)
                else:
                    continuation = _Loop(yes=False)

            case _:
                raise TypeError(f'{self.app.__name__}.handle_info did not return a valid value')

        return continuation, state
