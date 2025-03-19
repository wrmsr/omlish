"""
basedpyright 'pyright[nodejs]'
"""
import contextlib
import subprocess

import anyio.abc

from omlish import check
from omlish import marshal as msh

from .client import LspClient
from .data import InitializeParams
from .data import InitializeResult


##


async def _a_main_(aes: contextlib.AsyncExitStack) -> None:
    # tg: anyio.abc.TaskGroup = await aes.enter_async_context(anyio.create_task_group())  # noqa

    process = await anyio.open_process(
        [
            'pyright-langserver',
            # 'basedpyright-langserver',
            '--stdio',
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    await aes.enter_async_context(process)

    client = LspClient(
        check.not_none(process.stdin).send,
        check.not_none(process.stdout).receive,
    )

    init_response = await client.request('initialize', InitializeParams(
        process_id=None,
        root_uri='file:///tmp',
        capabilities={},
    ))
    init_result = msh.unmarshal(init_response.result, InitializeResult)
    print('LSP Initialized:', init_result)

    await client.notify('initialized')
    await anyio.sleep(.5)

    await client.request('shutdown', {})
    await client.notify('exit', {})
    await anyio.sleep(.5)

    await process.aclose()


async def _a_main() -> None:
    async with contextlib.AsyncExitStack() as aes:
        await _a_main_(aes)


if __name__ == '__main__':
    anyio.run(_a_main)
