from omcore.http.pipelines.servers.apps.asgi import IoPipelineAsgiSpec

from ..... import minichain as mc
from ..base import ChatInterface
from .app import ChatApp
from .configs import DEFAULT_PORT
from .pipelines import serve_asgi_pipeline
from .types import ServerPort


##


class WebChatInterface(ChatInterface):
    def __init__(
            self,
            *,
            app: ChatApp,
            driver: mc.drivers.Driver,
            port: ServerPort = ServerPort(DEFAULT_PORT),
    ) -> None:
        super().__init__()

        self._app = app
        self._driver = driver
        self._port = port

    async def run(self) -> None:
        port = self._port

        app_spec = IoPipelineAsgiSpec(self._app.handle, port=port)

        print(f'Launching server at http://localhost:{port}.')

        await self._driver.start()

        try:
            await serve_asgi_pipeline(app_spec)

        finally:
            await self._driver.stop()
