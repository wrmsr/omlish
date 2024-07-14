import contextlib
import logging
import threading
import typing as ta

import requests

from .. import check
from .. import configs as cfg
from .. import lang
from .. import lifecycles as lc
from .current import current
from .current import inherit_current


log = logging.getLogger(__name__)


class HttpPinger(cfg.Configurable, lc.ContextManageableLifecycle):

    class Config(cfg.Config):
        ping_interval: float = 1.
        grace_period: ta.Optional[float] = 5.

    class Method(lang.AutoEnum):
        GET = ...
        POST = ...

    class Target(ta.NamedTuple):
        method: 'HttpPinger.Method'
        url: str

    def __init__(
            self,
            target: ta.Union[Target, ta.Callable[[], requests.Response]],
            *,
            validator: ta.Optional[ta.Callable[[requests.Response], None]] = None,
            error_handler: ta.Optional[ta.Callable[[requests.Response], None]] = None,
            shutdown_event: ta.Optional[threading.Event] = None,
            config: Config = Config(),
    ) -> None:
        super().__init__(config)

        if isinstance(target, HttpPinger.Target):
            check.isinstance(target.method, HttpPinger.Method)
            check.isinstance(target.url, str)
        else:
            check.callable(target)
        if validator is not None:
            check.callable(validator)
        if error_handler is not None:
            check.callable(error_handler)
        if shutdown_event is None:
            shutdown_event = threading.Event()

        self._target = target
        self._validator = validator
        self._error_handler = error_handler
        self._shutdown_event = check.isinstance(shutdown_event, threading.Event)

        self._pinger: threading.Thread = threading.Thread(
            target=inherit_current(self._pinger_proc),
            name='WatchdogHttpPinger',
            daemon=True
        )

    def _do_lifecycle_start(self) -> None:
        self._pinger.start()

    def _do_lifecycle_stop(self) -> None:
        self._shutdown_event.set()

        if self._pinger.is_alive():
            self._pinger.join(self._config.ping_interval * 3)
            if self._pinger.is_alive():
                log.error('Failed to shutdown watchdog checker')

    def _pinger_proc(self):
        try:
            log.info('Watchdog http pinger started')

            if not self._shutdown_event.wait(self._config.grace_period or 0.):
                while not self._shutdown_event.wait(self._config.ping_interval):
                    try:
                        self.ping()
                    except Exception:
                        log.exception('Watchdog http pinger exception')

            log.info('Watchdog http pinger')

        except Exception:
            log.exception('Watchdog http pinger')
            raise

    def ping(self, *, grace: bool = False) -> None:
        target = self._target
        if isinstance(target, HttpPinger.Target):
            def run():
                if target.method == HttpPinger.Method.GET:
                    return requests.get(target.url)
                elif target.method == HttpPinger.Method.POST:
                    return requests.post(target.url)
                else:
                    raise ValueError(target.method)
        elif callable(target):
            run = target
        else:
            raise TypeError(target)

        with current().watch(self, meta={'target': target}):
            response: requests.Response
            with contextlib.closing(run()) as response:
                check.isinstance(response, requests.Response)
                if response.status_code != 200 and not grace:
                    log.error(f'Watchdog http pinger response error: {response}')

                    if self._error_handler is not None:
                        self._error_handler(response)
