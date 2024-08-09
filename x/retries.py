"""
TODO:
 - tenacity obv
 - coordination (redis? coord iface?)
 - dogpile
 - mv faults?

https://engineering.shopify.com/blogs/engineering/circuit-breaker-misconfigured
"""
import time
import typing as ta

from omlish import check
from omlish import lang


class Call:

    def __init__(
            self,
            retrier: 'Retrier',
            fn: ta.Callable,
            args: ta.Optional[ta.Iterable[ta.Any]] = None,
            kwargs: ta.Optional[ta.Mapping[str, ta.Any]] = None,
    ) -> None:
        super().__init__()

        self._retrier = check.isinstance(retrier, Retrier)
        self._fn = check.callable(fn)
        self._args = list(args or ())
        self._kwargs = dict(kwargs or {})

        self._start_time = time.time()

        # self._attempt_number = 1
        # self._outcome = None
        # self._outcome_timestamp = None
        # self._idle_for = 0.
        # self._next_action = None

    @classmethod
    def of(cls, retrier: 'Retrier', fn: ta.Callable, *args, **kwargs) -> 'Call':
        return cls(retrier, fn, args, kwargs)


class _ReprFn:

    def __init__(self, rpr: str, fn: ta.Callable) -> None:
        super().__init__()

        self._rpr = check.isinstance(rpr, str)
        self._fn = check.callable(fn)

    def __repr__(self) -> str:
        return self._rpr

    def __get__(self, instance, owner=None):
        return type(self)(self._rpr, self._fn.__get__(instance, owner))  # noqa

    def __call__(self, *args, **kwargs):
        return self._fn(*args, **kwargs)


def _repr_fn(rpr: str, fn: ta.Callable) -> ta.Callable:
    return _ReprFn(rpr, fn)


RetryFn = ta.Callable[['Call'], bool]
WaitFn = ta.Callable[['Call'], float]
StopFn = ta.Callable[['Call'], bool]
CallbackFn = ta.Callable[['RetryFn'], None]


class Retry(lang.Namespace):
    ALWAYS = _repr_fn('Retry.ALWAYS', lambda _: True)


class Wait(lang.Namespace):
    NONE = _repr_fn('Wait.NONE', lambda _: 0.)


class Stop(lang.Namespace):
    NEVER = _repr_fn('Stop.NEVER', lambda _: False)


class Retrier:

    def __init__(
            self,
            *,
            retry: RetryFn = Retry.ALWAYS,
            wait: WaitFn = Wait.NONE,
            stop: StopFn = Stop.NEVER,
            sleep: ta.Callable[[float], None] = time.sleep,
            before: ta.Optional[CallbackFn] = None,
            after: ta.Optional[CallbackFn] = None,
            reraise: bool = False,
    ) -> None:
        super().__init__()

        self._retry = check.callable(retry)
        self._wait = check.callable(wait)
        self._stop = check.callable(stop)
        self._sleep = check.callable(sleep)
        self._before = check.callable(before) if before is not None else None
        self._after = check.callable(after) if after is not None else None
        self._reraise = check.isinstance(reraise, bool)

        # before_sleep = None,
        # retry_error_cls = RetryError,
        # retry_error_callback = None,

    def call(self, fn: ta.Callable, *args, **kwargs) -> Call:
        return Call.of(self, fn, *args, **kwargs)

    def __call__(self, fn: ta.Callable, *args, **kwargs) -> Call:
        return self.call(fn, *args, **kwargs)
