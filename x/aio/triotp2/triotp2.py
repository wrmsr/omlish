import collections
import contextlib
import contextvars
import dataclasses as dc
import enum
import logging
import sys
import tenacity
import typing as ta
import uuid

import logbook
import trio

from .. import trio_util


# helpers


class Module:
    pass


# logging


class LogLevel(enum.Enum):
    NONE = enum.auto()  #: Logging is disabled
    DEBUG = enum.auto()
    INFO = enum.auto()
    WARNING = enum.auto()
    ERROR = enum.auto()
    CRITICAL = enum.auto()

    def to_logbook(self) -> int:
        return logging.getLevelNamesMapping[self.name]


def getLogger(name: str) -> logging.Logger:
    return logging.getLogger(name)


# mailbox


MailboxID = ta.TypeVar('MailboxID', bound=str)  #: Mailbox identifier (UUID4)


class Registry:
    def __init__(self):
        super().__init__()
        self.mailboxes = {}
        self.names = {}


context_registries = contextvars.ContextVar('registries')


class MailboxDoesNotExist(RuntimeError):
    def __init__(self, mid: MailboxID) -> None:
        super().__init__(f'mailbox {mid} does not exist')


class NameAlreadyExist(RuntimeError):
    def __init__(self, name: str) -> None:
        super().__init__(f'mailbox {name} already registered')


class NameDoesNotExist(RuntimeError):
    def __init__(self, name: str) -> None:
        super().__init__(f'mailbox {name} does not exist')


def _mailbox_init() -> None:
    context_registries.set(Registry())


def mailbox_create() -> MailboxID:
    mid = str(uuid.uuid4())

    mailbox_registry = context_registries.get().mailboxes
    mailbox_registry[mid] = trio.open_memory_channel(0)

    return mid


async def mailbox_destroy(mid: MailboxID) -> None:
    mailbox_registry = context_registries.get().mailboxes

    if mid not in mailbox_registry:
        raise MailboxDoesNotExist(mid)

    mailbox_unregister_all(mid)

    wchan, rchan = mailbox_registry.pop(mid)
    await wchan.aclose()
    await rchan.aclose()


def mailbox_register(mid: MailboxID, name: str) -> None:
    mailbox_registry = context_registries.get().mailboxes

    if mid not in mailbox_registry:
        raise MailboxDoesNotExist(mid)

    name_registry = context_registries.get().names
    if name in name_registry:
        raise NameAlreadyExist(name)

    name_registry[name] = mid


def mailbox_unregister(name: str) -> None:
    name_registry = context_registries.get().names
    if name not in name_registry:
        raise NameDoesNotExist(name)

    name_registry.pop(name)


def mailbox_unregister_all(mid: MailboxID) -> None:
    name_registry = context_registries.get().names

    for name, mailbox_id in list(name_registry.items()):
        if mailbox_id == mid:
            name_registry.pop(name)


@contextlib.asynccontextmanager
async def mailbox_open(name: str | None = None) -> ta.AsyncContextManager[MailboxID]:
    mid = mailbox_create()

    try:
        if name is not None:
            mailbox_register(mid, name)

        yield mid

    finally:
        await mailbox_destroy(mid)


def _mailbox_resolve(name: str) -> MailboxID | None:
    name_registry = context_registries.get().names
    return name_registry.get(name)


async def mailbox_send(name_or_mid: str | MailboxID, message: ta.Any) -> None:
    mailbox_registry = context_registries.get().mailboxes

    mid = _mailbox_resolve(name_or_mid)
    if mid is None:
        mid = name_or_mid

    if mid not in mailbox_registry:
        raise MailboxDoesNotExist(mid)

    wchan, _ = mailbox_registry.get(mid)
    await wchan.send(message)


async def mailbox_receive(
        mid: MailboxID,
        timeout: float | None = None,
        on_timeout: ta.Callable[[], ta.Awaitable[ta.Any]] = None,
) -> ta.Any:
    mailbox_registry = context_registries.get().mailboxes

    if mid not in mailbox_registry:
        raise MailboxDoesNotExist(mid)

    _, rchan = mailbox_registry.get(mid)

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


# supervisor


class restart_strategy(enum.Enum):
    PERMANENT = enum.auto()  #: Always restart the task
    TRANSIENT = enum.auto()  #: Restart the task only if it raises an exception
    TEMPORARY = enum.auto()  #: Never restart a task


@dc.dataclass()
class child_spec:
    id: str  #: Task identifier
    task: ta.Callable[..., ta.Awaitable[None]]  #: The task to run
    args: list[ta.Any]  #: Arguments to pass to the task
    restart: restart_strategy = restart_strategy.PERMANENT  #: When to restart the task


@dc.dataclass()
class supervisor_options:
    max_restarts: int = 3  #: Maximum number of restart during a limited timespan
    max_seconds: int = 5  #: Timespan duration


class _retry_strategy:
    def __init__(
            self,
            restart: restart_strategy,
            max_restarts: int,
            max_seconds: float,
    ) -> None:
        super().__init__()
        self.restart = restart
        self.max_restarts = max_restarts
        self.max_seconds = max_seconds

        self.failure_times = collections.deque()

    def __call__(self, retry_state: tenacity.RetryCallState):
        match self.restart:
            case restart_strategy.PERMANENT:
                pass

            case restart_strategy.TRANSIENT:
                if not retry_state.outcome.failed:
                    return False

            case restart_strategy.TEMPORARY:
                return False

        now = trio.current_time()
        self.failure_times.append(now)

        if len(self.failure_times) <= self.max_restarts:
            return True

        oldest_failure = self.failure_times.popleft()
        return now - oldest_failure >= self.max_seconds


class _retry_logger:
    def __init__(self, child_id: str) -> None:
        super().__init__()
        self.logger = logbook.Logger(child_id)

    def __call__(self, retry_state: tenacity.RetryCallState) -> None:
        if isinstance(retry_state.outcome.exception(), trio.Cancelled):
            self.logger.info('task cancelled')

        elif retry_state.outcome.failed:
            exception = retry_state.outcome.exception()
            exc_info = (exception.__class__, exception, exception.__traceback__)
            self.logger.error('restarting task after failure', exc_info=exc_info)

        else:
            self.logger.error('restarting task after unexpected exit')


async def supervisor_start(
        child_specs: list[child_spec],
        opts: supervisor_options,
        task_status=trio.TASK_STATUS_IGNORED,
) -> None:
    async with trio.open_nursery() as nursery:
        for spec in child_specs:
            await nursery.start(_supervisor_child_monitor, spec, opts)

        task_status.started(None)


async def _supervisor_child_monitor(
        spec: child_spec,
        opts: supervisor_options,
        task_status=trio.TASK_STATUS_IGNORED,
) -> None:
    task_status.started(None)

    @tenacity.retry(
        retry=_retry_strategy(spec.restart, opts.max_restarts, opts.max_seconds),
        reraise=True,
        sleep=trio.sleep,
        after=_retry_logger(spec.id),
    )
    async def _child_runner():
        with trio_util.defer_to_cancelled():
            async with trio.open_nursery() as nursery:
                nursery.start_soon(spec.task, *spec.args)

    await _child_runner()


# dynamic_supervisor


async def dynamic_supervisor_start(
        opts: supervisor_options,
        name: str | None = None,
        task_status=trio.TASK_STATUS_IGNORED,
) -> None:
    async with mailbox_open(name) as mid:
        task_status.started(mid)

        async with trio.open_nursery() as nursery:
            await nursery.start(_dynamic_supervisor_child_listener, mid, opts, nursery)


async def dynamic_supervisor_start_child(
        name_or_mid: str | MailboxID,
        child_spec: child_spec,
) -> None:
    await mailbox_send(name_or_mid, child_spec)


async def _dynamic_supervisor_child_listener(
        mid: MailboxID,
        opts: supervisor_options,
        nursery: trio.Nursery,
        task_status=trio.TASK_STATUS_IGNORED,
) -> None:
    task_status.started(None)

    while True:
        request = await mailbox_receive(mid)

        match request:
            case child_spec() as spec:
                await nursery.start(_supervisor_child_monitor, spec, opts)

            case _:
                pass


#


context_app_nursery = contextvars.ContextVar('app_nursery')
context_app_registry = contextvars.ContextVar('app_registry')


@dc.dataclass()
class app_spec:
    module: Module  #: Application module
    start_arg: ta.Any  #: Argument to pass to the module's start function
    permanent: bool = True  #: If `False`, the application won't be restarted if it exits
    opts: supervisor_options | None = None  #: Options for the supervisor managing the application task


def _application_init(nursery: trio.Nursery) -> None:
    context_app_nursery.set(nursery)
    context_app_registry.set({})


async def application_start(app: app_spec) -> None:
    nursery = context_app_nursery.get()
    registry = context_app_registry.get()

    if app.module.__name__ not in registry:
        local_nursery = await nursery.start(_app_scope, app)
        registry[app.module.__name__] = local_nursery


async def application_stop(app_name: str) -> None:
    registry = context_app_registry.get()

    if app_name in registry:
        local_nursery = registry.pop(app_name)
        local_nursery.cancel_scope.cancel()


async def _app_scope(app: app_spec, task_status=trio.TASK_STATUS_IGNORED):
    if app.permanent:
        restart = restart_strategy.PERMANENT

    else:
        restart = restart_strategy.TRANSIENT

    async with trio.open_nursery() as nursery:
        task_status.started(nursery)

        children = [
            child_spec(
                id=app.module.__name__,
                task=app.module.start,
                args=[app.start_arg],
                restart=restart,
            )
        ]
        opts = app.opts if app.opts is not None else supervisor_options()

        nursery.start_soon(supervisor_start, children, opts)


# node


def node_run(
        apps: list[app_spec],
        loglevel: LogLevel = LogLevel.NONE,
        logformat: str | None = None,
) -> None:
    match loglevel:
        case LogLevel.NONE:
            handler = logging.NullHandler()

        case _:
            handler = logging.StreamHandler(sys.stdout, level=loglevel.to_logbook())

    if logformat is not None:
        handler.format_string = logformat

    # with handler.applicationbound():  # FIXME
    trio.run(_node_start, apps)


async def _node_start(apps: list[app_spec]) -> None:
    _mailbox_init()

    async with trio.open_nursery() as nursery:
        _application_init(nursery)

        for app_spec in apps:
            await application_start(app_spec)


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
    payload: ta.Any  #: The response to send back


@dc.dataclass()
class NoReply:
    pass


@dc.dataclass()
class Stop:
    reason: BaseException | None =  None  #: Eventual exception that caused the gen_server to stop


@dc.dataclass()
class _CallMessage:
    source: trio.MemorySendChannel
    payload: ta.Any


@dc.dataclass()
class _CastMessage:
    payload: ta.Any


async def gen_server_start(
        module: Module,
        init_arg: ta.Any | None = None,
        name: str | None = None,
) -> None:
    await _gen_server_loop(module, init_arg, name)


async def gen_server_call(
        name_or_mid: str | MailboxID,
        payload: ta.Any,
        timeout: float | None = None,
) -> ta.Any:
    wchan, rchan = trio.open_memory_channel(0)
    message = _CallMessage(source=wchan, payload=payload)

    await mailbox_send(name_or_mid, message)

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


async def gen_server_cast(
        name_or_mid: str | MailboxID,
        payload: ta.Any,
) -> None:
    message = _CastMessage(payload=payload)
    await mailbox_send(name_or_mid, message)


async def gen_server_reply(caller: trio.MemorySendChannel, response: ta.Any) -> None:
    await caller.send(response)


async def _gen_server_loop(
        module: Module,
        init_arg: ta.Any | None,
        name: str | None,
) -> None:
    async with mailbox_open(name) as mid:
        try:
            state = await _gen_server_init(module, init_arg)
            looping = True

            while looping:
                message = await mailbox_receive(mid)

                match message:
                    case _CallMessage(source, payload):
                        continuation, state = await _gen_server_handle_call(
                            module, payload, source, state
                        )

                    case _CastMessage(payload):
                        continuation, state = await _gen_server_handle_cast(module, payload, state)

                    case _:
                        continuation, state = await _gen_server_handle_info(module, message, state)

                match continuation:
                    case _Loop(yes=False):
                        looping = False

                    case _Loop(yes=True):
                        looping = True

                    case _Raise(exc=err):
                        raise err

        except Exception as err:
            await _gen_server_terminate(module, err, state)
            raise err from None

        else:
            await _gen_server_terminate(module, None, state)


async def _gen_server_init(module: Module, init_arg: ta.Any) -> State:
    return await module.init(init_arg)


async def _gen_server_terminate(
        module: Module,
        reason: BaseException | None,
        state: State,
) -> None:
    handler = getattr(module, 'terminate', None)
    if handler is not None:
        await handler(reason, state)

    elif reason is not None:
        logger = logging.getLogger(module.__name__)
        logger.exception(reason)


async def _gen_server_handle_call(
        module: Module,
        message: ta.Any,
        source: trio.MemorySendChannel,
        state: State,
) -> tuple[Continuation, State]:
    handler = getattr(module, 'handle_call', None)
    if handler is None:
        raise NotImplementedError(f'{module.__name__}.handle_call')

    result = await handler(message, source, state)

    match result:
        case (Reply(payload), new_state):
            state = new_state
            await gen_server_reply(source, payload)
            continuation = _Loop(yes=True)

        case (NoReply(), new_state):
            state = new_state
            continuation = _Loop(yes=True)

        case (Stop(reason), new_state):
            state = new_state
            await gen_server_reply(source, GenServerExited())

            if reason is not None:
                continuation = _Raise(reason)

            else:
                continuation = _Loop(yes=False)

        case _:
            raise TypeError(
                f'{module.__name__}.handle_call did not return a valid value'
            )

    return continuation, state


async def _gen_server_handle_cast(
        module: Module,
        message: ta.Any,
        state: State,
) -> tuple[Continuation, State]:
    handler = getattr(module, 'handle_cast', None)
    if handler is None:
        raise NotImplementedError(f'{module.__name__}.handle_cast')

    result = await handler(message, state)

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
            raise TypeError(f'{module.__name__}.handle_cast did not return a valid value')

    return continuation, state


async def _gen_server_handle_info(
        module: Module,
        message: ta.Any,
        state: State,
) -> tuple[Continuation, State]:
    handler = getattr(module, 'handle_info', None)
    if handler is None:
        return _Loop(yes=True), state

    result = await handler(message, state)

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
            raise TypeError(f'{module.__name__}.handle_info did not return a valid value')

    return continuation, state
