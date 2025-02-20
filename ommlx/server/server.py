import dataclasses as dc
import logging
import time
import typing as ta

from omdev.home.secrets import load_secrets
from omlish import cached
from omlish import check
from omlish.http.coro.simple import make_simple_http_server
from omlish.http.handlers import HttpHandler_
from omlish.http.handlers import HttpHandlerRequest
from omlish.http.handlers import HttpHandlerResponse
from omlish.http.handlers import LoggingHttpHandler
from omlish.secrets.tests.harness import HarnessSecrets  # noqa
from omlish.sockets.bind import CanSocketBinderConfig
from omlish.sockets.bind import SocketBinder

from .. import minichain as mc
from ..minichain.backends.mlxlm import MlxlmChatModel
from ..minichain.backends.openai import OpenaiChatModel
from ..minichain.generative import Temperature


log = logging.getLogger(__name__)


##


@dc.dataclass(frozen=True)
class ServerHandler(HttpHandler_):
    llm: mc.ChatModel

    def __call__(self, req: HttpHandlerRequest) -> HttpHandlerResponse:
        prompt = check.not_none(req.data).decode('utf-8')

        log.info('Server got prompt: %s', prompt)

        resp = self.llm(
            [mc.UserMessage(prompt)],
            Temperature(.1),
        )
        resp_txt = check.not_none(resp.v[0].m.s)

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


class Server:
    @dc.dataclass(frozen=True)
    class Config:
        DEFAULT_BIND: ta.ClassVar[CanSocketBinderConfig] = 5067
        bind: SocketBinder.Config = SocketBinder.Config.of(DEFAULT_BIND)

        backend: ta.Literal['openai', 'local'] = 'openai'

    def __init__(self, config: Config = Config()) -> None:
        super().__init__()

        self._config = config

    @cached.function
    def llm(self) -> mc.ChatModel:
        if self._config.backend == 'openai':
            return OpenaiChatModel(api_key=load_secrets().get('openai_api_key').reveal())

        elif self._config.backend == 'local':
            return MlxlmChatModel()

        else:
            raise ValueError(self._config.backend)

    def run(self) -> None:
        log.info('Server running')
        try:

            llm = self.llm()

            with make_simple_http_server(
                    self._config.bind,
                    LoggingHttpHandler(ServerHandler(llm), log),
            ) as server:

                deadline = time.time() + 60.
                with server.loop_context(poll_interval=5.) as loop:
                    for _ in loop:
                        if time.time() >= deadline:
                            break

        finally:
            log.info('Server exiting')

    @classmethod
    def run_config(cls, config: Config) -> None:
        return cls(config).run()
