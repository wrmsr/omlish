"""
basedpyright 'pyright[nodejs]'
"""
import contextlib
import subprocess

import anyio.abc

from omlish import check
from omlish import marshal as msh

from .client import LspClient
from .data import DefinitionResponse
from .data import DidOpenTextDocumentParams
from .data import InitializeParams
from .data import InitializeResult
from .data import Position
from .data import TextDocumentIdentifier
from .data import TextDocumentItem
from .data import TextDocumentPositionParams


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
    print(init_result)

    await client.notify('initialized')
    await anyio.sleep(.5)

    #

    # Simulated Python file content
    python_code = """
def foo():
    return 42

foo()
    """.strip()

    file_uri = 'file:///tmp/example.py'

    await client.notify('textDocument/didOpen', DidOpenTextDocumentParams(
        text_document=TextDocumentItem(
            uri=file_uri,
            language_id='python',
            version=1,
            text=python_code,
        ),
    ))

    definition_response = await client.request('textDocument/definition', TextDocumentPositionParams(
        text_document=TextDocumentIdentifier(uri=file_uri),
        position=Position(line=3, character=1),
    ))
    definition_result: DefinitionResponse = msh.unmarshal(definition_response.result, DefinitionResponse)  # type: ignore  # noqa

    for loc in definition_result or []:
        print(loc)

    #

    await client.request('shutdown', {})
    await client.notify('exit', {})
    await anyio.sleep(.5)

    await process.aclose()


async def _a_main() -> None:
    async with contextlib.AsyncExitStack() as aes:
        await _a_main_(aes)


if __name__ == '__main__':
    anyio.run(_a_main)
