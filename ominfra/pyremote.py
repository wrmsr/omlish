# ruff: noqa: UP006 UP007
# @omlish-lite
"""
Basically this: https://mitogen.networkgenomics.com/howitworks.html
"""
import base64
import dataclasses as dc
import inspect
import json
import os
import struct
import sys
import textwrap
import typing as ta
import zlib

from omlish.lite.check import check_isinstance
from omlish.lite.check import check_none


##


_PYREMOTE_BOOTSTRAP_COMM_FD = 100
_PYREMOTE_BOOTSTRAP_SRC_FD = 101

_PYREMOTE_BOOTSTRAP_CHILD_PID_VAR = '_OPYR_CPID'
_PYREMOTE_BOOTSTRAP_ARGV0_VAR = '_OPYR_ARGV0'

_PYREMOTE_BOOTSTRAP_ACK0 = b'OPYR000\n'
_PYREMOTE_BOOTSTRAP_ACK1 = b'OPYR001\n'
_PYREMOTE_BOOTSTRAP_ACK2 = b'OPYR001\n'
_PYREMOTE_BOOTSTRAP_ACK3 = b'OPYR001\n'

_PYREMOTE_BOOTSTRAP_PROC_TITLE_FMT = '(pyremote:%s)'

_PYREMOTE_BOOTSTRAP_IMPORTS = [
    'base64',
    'os',
    'struct',
    'sys',
    'zlib',
]


def _pyremote_bootstrap_main(context_name: str) -> None:
    # Get pid
    pid = os.getpid()

    # Two copies of main src to be sent to parent
    r0, w0 = os.pipe()
    r1, w1 = os.pipe()

    if (cp := os.fork()):
        # Parent process

        # Dup original stdin to comm_fd for use as comm channel
        os.dup2(0, _PYREMOTE_BOOTSTRAP_COMM_FD)

        # Overwrite stdin (fed to python repl) with first copy of src
        os.dup2(r0, 0)

        # Dup second copy of src to src_fd to recover after launch
        os.dup2(r1, _PYREMOTE_BOOTSTRAP_SRC_FD)

        # Close remaining fd's
        for f in [r0, w0, r1, w1]:
            os.close(f)

        # Save child pid to close after relaunch
        os.environ[_PYREMOTE_BOOTSTRAP_CHILD_PID_VAR] = str(cp)

        # Save original argv0
        os.environ[_PYREMOTE_BOOTSTRAP_ARGV0_VAR] = sys.executable

        # Start repl reading stdin from r0
        os.execl(sys.executable, sys.executable + (_PYREMOTE_BOOTSTRAP_PROC_TITLE_FMT % (context_name,)))

    else:
        # Child process

        # Write first ack
        os.write(1, _PYREMOTE_BOOTSTRAP_ACK0)

        # Write pid
        os.write(1, struct.pack('<Q', pid))

        # Read main src from stdin
        main_z_len = struct.unpack('<I', os.read(0, 4))[0]
        main_src = zlib.decompress(os.fdopen(0, 'rb').read(main_z_len))

        # Write both copies of main src. Must write to w0 (parent stdin) before w1 (copy pipe) as pipe will likely fill
        # and block and need to be drained by pyremote_bootstrap_finalize running in parent.
        for w in [w0, w1]:
            fp = os.fdopen(w, 'wb', 0)
            fp.write(main_src)
            fp.close()

        # Write second ack
        os.write(1, _PYREMOTE_BOOTSTRAP_ACK1)

        sys.exit(0)


##


def pyremote_build_bootstrap_cmd(context_name: str) -> str:
    bs_src = textwrap.dedent(inspect.getsource(_pyremote_bootstrap_main))

    for gl in [
        '_PYREMOTE_BOOTSTRAP_COMM_FD',
        '_PYREMOTE_BOOTSTRAP_SRC_FD',

        '_PYREMOTE_BOOTSTRAP_CHILD_PID_VAR',
        '_PYREMOTE_BOOTSTRAP_ARGV0_VAR',

        '_PYREMOTE_BOOTSTRAP_ACK0',
        '_PYREMOTE_BOOTSTRAP_ACK1',

        '_PYREMOTE_BOOTSTRAP_PROC_TITLE_FMT',
    ]:
        bs_src = bs_src.replace(gl, repr(globals()[gl]))

    bs_src = '\n'.join(
        cl
        for l in bs_src.splitlines()
        if (cl := (l.split('#')[0]).rstrip())
        if cl.strip()
    )

    bs_z = zlib.compress(bs_src.encode('utf-8'))
    bs_z64 = base64.encodebytes(bs_z).replace(b'\n', b'')

    stmts = [
        f'import {", ".join(_PYREMOTE_BOOTSTRAP_IMPORTS)}',
        f'exec(zlib.decompress(base64.decodebytes({bs_z64!r})))',
        f'_pyremote_bootstrap_main({context_name!r})',
    ]

    cmd = '; '.join(stmts)
    return cmd


##


@dc.dataclass(frozen=True)
class PyremoteEnvInfo:
    platform: str


def _get_pyremote_env_info() -> PyremoteEnvInfo:
    return PyremoteEnvInfo(
        platform=sys.platform,
    )


##


class PyremoteBootstrapDriver:
    def __init__(self, main_src: str) -> None:
        super().__init__()

        self._main_src = main_src
        self._main_z = zlib.compress(main_src.encode('utf-8'))

    @dc.dataclass(frozen=True)
    class Read:
        sz: int

    @dc.dataclass(frozen=True)
    class Write:
        d: bytes

    class ProtocolError(Exception):
        pass

    @dc.dataclass(frozen=True)
    class Result:
        pid: int
        env_info: PyremoteEnvInfo

    def __call__(self) -> ta.Generator[ta.Union[Read, Write], ta.Optional[bytes], Result]:
        yield from self._expect(_PYREMOTE_BOOTSTRAP_ACK0)

        d = yield from self._read(8)
        pid = struct.unpack('<Q', d)[0]

        check_none((yield self.Write(struct.pack('<I', len(self._main_z)))))
        check_none((yield self.Write(self._main_z)))

        yield from self._expect(_PYREMOTE_BOOTSTRAP_ACK1)
        yield from self._expect(_PYREMOTE_BOOTSTRAP_ACK2)

        d = yield from self._read(4)
        env_info_json_len = struct.unpack('<I', d)[0]
        d = yield from self._read(env_info_json_len)
        env_info_json = d.decode('utf-8')
        env_info = PyremoteEnvInfo(**json.loads(env_info_json))

        yield from self._expect(_PYREMOTE_BOOTSTRAP_ACK3)

        return self.Result(
            pid=pid,
            env_info=env_info,
        )

    def _expect(self, e: bytes) -> ta.Generator[Read, bytes, None]:
        d = check_isinstance((yield self.Read(len(e))), bytes)
        if d != e:
            raise self.ProtocolError

    def _read(self, sz: int) -> ta.Generator[Read, bytes, bytes]:
        return check_isinstance((yield self.Read(sz)), bytes)


##


@dc.dataclass(frozen=True)
class PyremoteBootstrapPayloadRuntime:
    input: ta.BinaryIO
    main_src: str


def pyremote_bootstrap_finalize() -> PyremoteBootstrapPayloadRuntime:
    # Restore original argv0
    sys.executable = os.environ.pop(_PYREMOTE_BOOTSTRAP_ARGV0_VAR)

    # Read second copy of main src
    r1 = os.fdopen(_PYREMOTE_BOOTSTRAP_SRC_FD, 'rb', 0)
    main_src = r1.read().decode('utf-8')
    r1.close()

    # Reap boostrap child. Must be done after reading second copy of source because source may be too big to fit in a
    # pipe at once.
    os.waitpid(int(os.environ.pop(_PYREMOTE_BOOTSTRAP_CHILD_PID_VAR)), 0)

    # Write third ack
    os.write(1, _PYREMOTE_BOOTSTRAP_ACK2)

    env_info = _get_pyremote_env_info()
    env_info_json = json.dumps(dc.asdict(env_info), indent=None, separators=(',', ':'))
    os.write(1, struct.pack('<I', len(env_info_json)))
    os.write(1, env_info_json.encode('utf-8'))

    # Write fourth ack
    os.write(1, _PYREMOTE_BOOTSTRAP_ACK3)

    return PyremoteBootstrapPayloadRuntime(
        input=os.fdopen(_PYREMOTE_BOOTSTRAP_COMM_FD, 'rb', 0),
        main_src=main_src,
    )
