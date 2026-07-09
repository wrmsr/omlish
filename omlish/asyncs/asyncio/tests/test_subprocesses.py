import pytest

from .... import check
from ..subprocesses import asyncio_subprocesses


##


@pytest.mark.asyncs('asyncio')
async def test_subprocesses():
    out = await asyncio_subprocesses.check_output('echo 42', shell=True)
    assert int(out.decode().strip()) == 42
    assert check.not_none(await asyncio_subprocesses.try_output('echo', 'hi')).decode() == 'hi\n'
    assert (await asyncio_subprocesses.try_output('xcho', 'hi')) is None
