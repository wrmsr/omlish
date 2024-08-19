#!/usr/bin/env python3
# @omdev-amalg ./_payload.py
"""
TODO:
 - fix stdio/stdout/stderr confusion - why writing results to stderr? and tracebacks clobber it
"""
# ruff: noqa: UP007
import dataclasses as dc
import io
import json
import subprocess
import sys
import typing as ta

from omlish.lite.json import json_dumps_compact
from omlish.lite.marshal import marshal_obj
from omlish.lite.marshal import unmarshal_obj
from omlish.lite.subprocesses import subprocess_maybe_shell_wrap_exec

from .bootstrap import post_boostrap


@dc.dataclass(frozen=True)
class CommandRequest:
    cmd: ta.Sequence[str]
    in_: ta.Optional[bytes] = None


@dc.dataclass(frozen=True)
class CommandResponse:
    req: CommandRequest
    rc: int
    out: bytes
    err: bytes


def _payload_loop(input: ta.BinaryIO, output: ta.BinaryIO = sys.stderr.buffer) -> None:  # noqa
    while (l := input.readline().decode('utf-8').strip()):
        req: CommandRequest = unmarshal_obj(json.loads(l), CommandRequest)
        proc = subprocess.Popen(  # type: ignore
            subprocess_maybe_shell_wrap_exec(req.cmd),
            **(dict(stdin=io.BytesIO(req.in_)) if req.in_ is not None else {}),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = proc.communicate()
        resp = CommandResponse(
            req=req,
            rc=proc.returncode,
            out=out,  # noqa
            err=err,  # noqa
        )
        output.write(json_dumps_compact(marshal_obj(resp)).encode('utf-8'))
        output.write(b'\n')
        output.flush()


def payload_main() -> None:
    bs = post_boostrap()
    _payload_loop(bs.input)
