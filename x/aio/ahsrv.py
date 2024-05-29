import abc
import asyncio
import typing as ta

import aiohttp.web as aw


class Handler(abc.ABC):
    @abc.abstractmethod
    async def __call__(self, request: aw.Request) -> aw.StreamResponse:
        raise NotImplementedError


class HelloHandler(Handler):
    async def __call__(self, request: aw.Request) -> aw.StreamResponse:
        return aw.Response(text='Hello, World!')


async def a_run_app(app: ta.Any, **kwargs: ta.Any) -> None:
    main_task = asyncio.get_event_loop().create_task(aw._run_app(app, **kwargs))  # noqa
    try:
        await main_task
    except (aw.GracefulExit, KeyboardInterrupt):
        pass
    finally:
        main_task.cancel()


async def _a_main() -> None:
    app = aw.Application()
    app.add_routes([aw.get('/', HelloHandler())])

    await a_run_app(app)


if __name__ == '__main__':
    asyncio.run(_a_main())
