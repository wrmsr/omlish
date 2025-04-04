"""
TODO:
 - use omserv
  - core daemon service skeleton should interop with simple server
"""
import dataclasses as dc
import logging
import time
import typing as ta

from omdev.home.secrets import load_secrets
from omlish import cached
from omlish import check
from omlish.http.coro.simple import make_simple_http_server
from omlish.http.handlers import ExceptionLoggingHttpHandler
from omlish.http.handlers import HttpHandler_
from omlish.http.handlers import HttpHandlerRequest
from omlish.http.handlers import HttpHandlerResponse
from omlish.http.handlers import LoggingHttpHandler
from omlish.sockets.bind import CanSocketBinderConfig
from omlish.sockets.bind import SocketBinder
from omlish.sockets.server.server import SocketServer

from .. import minichain as mc
from ..minichain.backends.mlx import MlxChatService
from ..minichain.backends.openai.chat import OpenaiChatService


log = logging.getLogger(__name__)


##


@dc.dataclass(frozen=True)
class McServerHandler(HttpHandler_):
    llm: mc.ChatService

    def __call__(self, req: HttpHandlerRequest) -> HttpHandlerResponse:
        prompt = check.not_none(req.data).decode('utf-8')

        log.info('Server got prompt: %s', prompt)

        resp = self.llm(
            [mc.UserMessage(prompt)],
            # Temperature(.1),
        )
        resp_txt = check.not_none(resp.choices[0].m.s)

        log.info('Server got response: %s', resp_txt)

        data = resp_txt.encode('utf-8')
        return HttpHandlerResponse(
            status=200,
            headers={
                'Content-Length': str(len(data)),
            },
            data=data,
            close_connection=True,
        )


class McServer:
    @dc.dataclass(frozen=True)
    class Config:
        DEFAULT_BIND: ta.ClassVar[CanSocketBinderConfig] = 5067
        bind: SocketBinder.Config = SocketBinder.Config.of(DEFAULT_BIND)

        backend: ta.Literal['openai', 'local'] = 'local'

        linger_s: float | None = 10 * 60.

    def __init__(self, config: Config = Config()) -> None:
        super().__init__()

        self._config = config

    @cached.function
    def llm(self) -> mc.ChatService:
        if self._config.backend == 'openai':
            return OpenaiChatService(api_key=load_secrets().get('openai_api_key').reveal())

        elif self._config.backend == 'local':
            model = 'mlx-community/Qwen2.5-Coder-32B-Instruct-8bit'
            return MlxChatService(model)

        else:
            raise ValueError(self._config.backend)

    def run(self) -> None:
        log.info('Server running')

        try:
            llm = self.llm()

            with make_simple_http_server(
                    self._config.bind,
                    ExceptionLoggingHttpHandler(
                        LoggingHttpHandler(
                            McServerHandler(llm),
                            log,
                        ),
                        log,
                    ),
            ) as server:
                if (linger_s := self._config.linger_s) is None:
                    linger_s = float('inf')

                deadline = time.monotonic() + linger_s

                with server.poll_context() as pc:
                    while True:
                        if time.monotonic() >= deadline:
                            log.info('Linger deadline exceeded')
                            break

                        res = pc.poll(5.)

                        if res in (SocketServer.PollResult.ERROR, SocketServer.PollResult.SHUTDOWN):
                            break

                        if res == SocketServer.PollResult.CONNECTION:
                            deadline = time.monotonic() + linger_s

        finally:
            log.info('Server exiting')

    @classmethod
    def run_config(cls, config: Config) -> None:
        return cls(config).run()
