# ruff: noqa: UP006 UP045
# @omlish-lite
import asyncio

from .....logs.std.standard import configure_standard_logging
from .clients import asyncio_fetch_url
from .clients import print_full_response


##


async def _a_main(url: str = 'http://httpbingo.org/gzip') -> None:
    resp = await asyncio_fetch_url(
        url,

        # with_flow=True,
        # flow_auto_read=False,

        with_gzip=True,
    )

    print_full_response(resp)


def _main() -> None:
    asyncio.run(_a_main())


if __name__ == '__main__':
    configure_standard_logging('debug')

    # try:
    #     __import__('omlish.check')
    # except ImportError:
    #     pass

    _main()
