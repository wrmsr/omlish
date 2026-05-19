from omlish.http.apps.tests.foo import build_foo_app


##


async def _a_main() -> None:
    import functools

    import anyio

    from omlish.sockets.ports import get_available_port

    from ...server.config import Config
    from ...server.default import serve
    from ...server.types import AsgiWrapper

    app = build_foo_app()

    port = get_available_port()
    server_bind = f'127.0.0.1:{port}'
    base_url = f'http://{server_bind}/'

    async with anyio.create_task_group() as tg:
        tg.start_soon(functools.partial(
            serve,
            AsgiWrapper(app),  # noqa
            Config(
                bind=(server_bind,),
            ),
        ))

        print(f'Serving at {base_url}')


if __name__ == '__main__':
    import anyio

    anyio.run(_a_main)
