import typing as ta

from omdev.home.secrets import install_env_secrets
from omlish.http.pipelines.servers.apps.asgi import AsgiSpec
from omlish.io.pipelines.asyncs import AsyncIoPipelineMessages  # noqa

from .chat import ChatCompletionsHandler
from .pipelines import serve_asgi_pipeline
from .serving import serve_data_cache_url
from .serving import serve_not_found
from .serving import serve_resource


##


_RESOURCE_ROUTES: ta.Mapping[str, tuple[str, str]] = {
    '/': ('index.html', 'text/html'),

    '/index.css': ('index.css', 'text/css'),

    '/sse-decoder.js': ('sse-decoder.js', 'application/javascript'),
    '/chat-app.js': ('chat-app.js', 'application/javascript'),
}

_DATA_CACHE_URL_ROUTES: ta.Mapping[str, tuple[str, str]] = {
    '/marked.js': ('https://cdn.jsdelivr.net/npm/marked@11.1.1/marked.min.js', 'application/javascript'),

    '/alpine.js': ('https://cdn.jsdelivr.net/npm/alpinejs@3.15.10/dist/cdn.min.js', 'application/javascript'),
}


class App:
    def __init__(
            self,
            *,
            chat_completions_handler: ChatCompletionsHandler,
    ) -> None:
        super().__init__()

        self._chat_completions_handler = chat_completions_handler

    async def handle(self, scope, receive, send):
        if scope['type'] != 'http':
            return

        method = scope.get('method')
        path = scope.get('path')

        if method == 'GET' and (rsrc_rt := _RESOURCE_ROUTES.get(path)) is not None:
            await serve_resource(send, *rsrc_rt)

        elif method == 'GET' and (dcu_rt := _DATA_CACHE_URL_ROUTES.get(path)) is not None:
            await serve_data_cache_url(send, *dcu_rt)

        elif (method, path) == ('POST', '/v1/chat/completions'):
            await self._chat_completions_handler.handle(receive, send)

        else:
            await serve_not_found(send)


##


def _main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=int, nargs='?')
    args = parser.parse_args()

    install_env_secrets('openai_api_key')

    app = App(
        chat_completions_handler=ChatCompletionsHandler(),
    )

    app_spec = AsgiSpec(app.handle, port=args.port or 8087)

    serve_asgi_pipeline(app_spec)


if __name__ == '__main__':
    _main()
