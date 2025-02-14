import dataclasses as dc
import logging
import time

from omlish.http.coro.simple import make_simple_http_server
from omlish.http.handlers import HttpHandlerRequest
from omlish.http.handlers import HttpHandlerResponse
from omlish.http.handlers import HttpHandler_
from omlish.secrets.tests.harness import HarnessSecrets  # noqa
from omlish.sockets.bind import SocketBinder
from ommlx.minichain.backends.openai import OpenaiChatModel
from ommlx.minichain.chat import ChatModel
from ommlx.minichain.chat import UserMessage
from ommlx.minichain.generative import Temperature


log = logging.getLogger(__name__)


##


PORT = 5066


@dc.dataclass(frozen=True)
class LlmServerHandler(HttpHandler_):
    llm: ChatModel

    def __call__(self, req: HttpHandlerRequest) -> HttpHandlerResponse:
        prompt = req.data.decode('utf-8')

        log.info(f'Server got prompt: %s', prompt)

        resp = self.llm(
            [UserMessage(prompt)],
            Temperature(.1),
        )
        resp_txt = resp.v[0].m.s

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


def llm_server_main() -> None:
    log.info('Server running')
    try:

        llm = OpenaiChatModel(api_key=HarnessSecrets().get_or_skip('openai_api_key').reveal())

        with make_simple_http_server(
                SocketBinder.Config.of(PORT),
                LlmServerHandler(llm),
        ) as server:

            deadline = time.time() + 10.
            with server.loop_context(poll_interval=5.) as loop:
                for _ in loop:
                    if time.time() >= deadline:
                        break

    finally:
        log.info('Server exiting')
