from omdev.home.secrets import install_env_secrets
from omlish.http.pipelines.servers.apps.asgi import AsgiSpec

from .app import ChatApp
from .chat import ChatCompletionsHandler
from .pipelines import serve_asgi_pipeline


##


def _main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=int, nargs='?')
    args = parser.parse_args()

    install_env_secrets('openai_api_key')

    app = ChatApp(
        chat_completions_handler=ChatCompletionsHandler(),
    )

    app_spec = AsgiSpec(app.handle, port=args.port or 8087)

    serve_asgi_pipeline(app_spec)


if __name__ == '__main__':
    _main()
