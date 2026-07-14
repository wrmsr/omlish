import io
import subprocess
import typing as ta

import anyio.abc

from ... import check
from ...lite.timeouts import Timeout
from ...subprocesses.asyncs import AbstractAsyncSubprocesses
from ...subprocesses.run import SubprocessRun
from ...subprocesses.run import SubprocessRunOutput


T = ta.TypeVar('T')


##


class AnyioSubprocesses(AbstractAsyncSubprocesses):
    async def run_(self, run: SubprocessRun) -> SubprocessRunOutput:
        kwargs = dict(run.kwargs or {})

        if run.capture_output:
            kwargs.setdefault('stdout', subprocess.PIPE)
            kwargs.setdefault('stderr', subprocess.PIPE)

        with anyio.fail_after(Timeout.of(run.timeout).or_(None)):
            async with await anyio.open_process(
                    run.cmd,
                    **kwargs,
            ) as proc:
                async def read_output(stream: anyio.abc.ByteReceiveStream, writer: ta.IO) -> None:
                    while True:
                        try:
                            data = await stream.receive()
                        except anyio.EndOfStream:
                            return
                        writer.write(data)

                stdout: io.BytesIO | None = None
                stderr: io.BytesIO | None = None
                async with anyio.create_task_group() as tg:
                    if proc.stdout is not None:
                        stdout = io.BytesIO()
                        tg.start_soon(read_output, proc.stdout, stdout)

                    if proc.stderr is not None:
                        stderr = io.BytesIO()
                        tg.start_soon(read_output, proc.stderr, stderr)

                    if proc.stdin and run.input is not None:
                        await proc.stdin.send(run.input)
                        await proc.stdin.aclose()

                    await proc.wait()

        if run.check and proc.returncode != 0:
            raise subprocess.CalledProcessError(
                ta.cast(int, proc.returncode),
                run.cmd,
                stdout.getvalue() if stdout is not None else None,
                stderr.getvalue() if stderr is not None else None,
            )

        return SubprocessRunOutput(
            proc=proc,

            returncode=check.isinstance(proc.returncode, int),

            stdout=stdout.getvalue() if stdout is not None else None,
            stderr=stderr.getvalue() if stderr is not None else None,
        )


anyio_subprocesses = AnyioSubprocesses()
