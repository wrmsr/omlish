#!/usr/bin/env python3
# @omdev-amalg ./_payload.py
import dataclasses as dc
import io
import json
import subprocess
import sys
import typing as ta

from omlish.lite.json import json_dumps_compact
from omlish.lite.marshal import marshal_obj
from omlish.lite.marshal import unmarshal_obj

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


def _payload_loop(input: ta.IO) -> None:
    while (l := input.readline()):
        req = unmarshal_obj(json.loads(l.decode('utf-8')), CommandRequest)
        proc = subprocess.Popen(
            req.cmd,
            **(dict(stdin=io.BytesIO(req.in_)) if req.in_ is not None else {}),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = proc.communicate()
        resp = CommandResponse(
            req=req,
            rc=proc.returncode,
            out=out,
            err=err,
        )
        print(json_dumps_compact(marshal_obj(resp)), file=sys.stderr)


def payload_main() -> None:
    bs = post_boostrap()
    _payload_loop(bs.input)
