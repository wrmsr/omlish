import pytest

from ..bisync import make_bisync_logger
from ..modules import get_module_loggers


@pytest.mark.asyncs('asyncio')
async def test_bisync() -> None:
    blog = make_bisync_logger(*get_module_loggers(globals()))
    blog.info('hi')
    await blog.a.info('hi')
    blog.a.s.info('hi')
