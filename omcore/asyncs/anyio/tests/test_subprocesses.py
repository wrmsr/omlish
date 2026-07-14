import pytest

from ..subprocesses import anyio_subprocesses


@pytest.mark.asyncs
async def test_subprocesses():
    res = await anyio_subprocesses.run(
        'echo',
        'hi',
        capture_output=True,
    )
    print(res)
