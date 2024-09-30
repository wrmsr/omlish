import json
import os.path
import sys
import typing as ta

import anyio.abc
import anyio.streams.buffered

from omlish.formats import json


class Server:
    def __init__(self) -> None:
        super().__init__()

    _proc: anyio.abc.Process

    async def __aenter__(self) -> ta.Self:
        self._proc = await anyio.open_process(
            'jedi-language-server',
            stderr=sys.stderr,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._proc.terminate()
        await self._proc.wait()


DEFAULT_CONTENT_TYPE = 'application/vscode-jsonrpc; charset=utf-8'


def encode_message(
        payload: ta.Any,
        *,
        content_type: str = DEFAULT_CONTENT_TYPE,
        headers: ta.Sequence[str] | None = None,
) -> bytes:
    body = json.dumps_compact(payload)
    return b'\r\n'.join(s.encode('utf-8') for s in [
        f'Content-Length: {len(body)}',
        f'Content-Type: {content_type}',
        *(headers or []),
        '',
        body,
    ])


CONTENT_LENGTH_PREFIX = b'Content-Length: '


def split_content_length(line: bytes) -> int | None:
    if not line.startswith(CONTENT_LENGTH_PREFIX):
        return None

    value = line.partition(CONTENT_LENGTH_PREFIX)[2].strip()
    return int(value)


async def _main() -> None:
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    os.chdir(root_dir)

    async with Server() as server:
        proc = server._proc  # noqa

        msg = {'id': 1, 'jsonrpc': '20', 'method': 'initialize', 'params': {'rootPath': root_dir}}

        await proc.stdin.send(encode_message(msg))
        # FIXME: flush??

        buffered = anyio.streams.buffered.BufferedByteReceiveStream(proc.stdout)  # noqa

        async def readline(max_bytes: int = 1024 * 1024) -> bytes:
            return await buffered.receive_until(b'\n', max_bytes)

        line = await readline()
        num_bytes = split_content_length(line)
        while line and line.strip():
            line = await readline()
        body = await buffered.receive_exactly(num_bytes)
        print(body)

        await anyio.sleep(3)


if __name__ == '__main__':
    anyio.run(_main)
