# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import asyncio
import typing as ta

from ...lite.timeouts import Timeout
from ...lite.timeouts import TimeoutLike


##


async def asyncio_wait_until_can_connect(
        host: ta.Any = None,
        port: ta.Any = None,
        *,
        timeout: TimeoutLike = None,
        on_fail: ta.Optional[ta.Callable[[BaseException], None]] = None,
        sleep_s: float = .1,
        exception: ta.Union[ta.Type[BaseException], ta.Tuple[ta.Type[BaseException], ...]] = (Exception,),
) -> None:
    timeout = Timeout.of(timeout)

    async def inner():
        while True:
            timeout()

            try:
                reader, writer = await asyncio.open_connection(host, port)

            except asyncio.CancelledError:
                raise

            except exception as e:  # noqa
                if on_fail is not None:
                    on_fail(e)

            else:
                writer.close()
                await asyncio.wait_for(writer.wait_closed(), timeout=timeout.or_(None))
                break

            await asyncio.sleep(min(sleep_s, timeout.remaining()))

    if timeout() != float('inf'):
        await asyncio.wait_for(inner(), timeout=timeout())
    else:
        await inner()
