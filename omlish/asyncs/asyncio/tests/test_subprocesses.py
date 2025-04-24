import pytest

from ..subprocesses import asyncio_subprocesses


@pytest.mark.asyncs('asyncio')
async def test_subprocesses():
    out = await asyncio_subprocesses.check_output('echo 42', shell=True)
    assert int(out.decode().strip()) == 42
