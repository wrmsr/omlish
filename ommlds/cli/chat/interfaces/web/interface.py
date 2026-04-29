from omlish.http.pipelines.servers.apps.asgi import AsgiSpec

from ..base import ChatInterface
from .app import ChatApp
from .chat import ChatCompletionsHandler
from .configs import DEFAULT_PORT
from .pipelines import serve_asgi_pipeline
from .types import ServerPort


##


class WebChatInterface(ChatInterface):
    def __init__(
            self,
            *,
            port: ServerPort = ServerPort(DEFAULT_PORT),
    ) -> None:
        super().__init__()

        self._port = port

    async def run(self) -> None:
        port = self._port

        app = ChatApp(
            chat_completions_handler=ChatCompletionsHandler(),
        )

        app_spec = AsgiSpec(app.handle, port=port)

        print(f'Launching server at http://localhost:{port}.')

        await serve_asgi_pipeline(app_spec)
