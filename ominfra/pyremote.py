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
import platform
import pwd
import site
import struct
import sys
import textwrap
import typing as ta
import zlib


##


_PYREMOTE_BOOTSTRAP_COMM_FD = 100
_PYREMOTE_BOOTSTRAP_SRC_FD = 101

_PYREMOTE_BOOTSTRAP_CHILD_PID_VAR = '_OPYR_CPID'
_PYREMOTE_BOOTSTRAP_ARGV0_VAR = '_OPYR_ARGV0'

_PYREMOTE_BOOTSTRAP_ACK0 = b'OPYR000\n'
_PYREMOTE_BOOTSTRAP_ACK1 = b'OPYR001\n'
_PYREMOTE_BOOTSTRAP_ACK2 = b'OPYR002\n'
_PYREMOTE_BOOTSTRAP_ACK3 = b'OPYR003\n'

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

        # Exit child
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
    sys_base_prefix: str
    sys_byteorder: str
    sys_defaultencoding: str
    sys_exec_prefix: str
    sys_executable: str
    sys_implementation_name: str
    sys_path: ta.List[str]
    sys_platform: str
    sys_prefix: str
    sys_version: str
    sys_version_info: ta.List[ta.Union[int, str]]

    platform_architecture: ta.List[str]
    platform_machine: str
    platform_platform: str
    platform_processor: str
    platform_system: str
    platform_release: str
    platform_version: str

    site_userbase: str

    os_cwd: str
    os_gid: int
    os_loadavg: ta.List[float]
    os_login: ta.Optional[str]
    os_pgrp: int
    os_pid: int
    os_ppid: int
    os_uid: int

    pw_name: str
    pw_uid: int
    pw_gid: int
    pw_gecos: str
    pw_dir: str
    pw_shell: str

    env_path: ta.Optional[str]


def _get_pyremote_env_info() -> PyremoteEnvInfo:
    os_uid = os.getuid()

    pw = pwd.getpwuid(os_uid)

    os_login: ta.Optional[str]
    try:
        os_login = os.getlogin()
    except OSError:
        os_login = None

    return PyremoteEnvInfo(
        sys_base_prefix=sys.base_prefix,
        sys_byteorder=sys.byteorder,
        sys_defaultencoding=sys.getdefaultencoding(),
        sys_exec_prefix=sys.exec_prefix,
        sys_executable=sys.executable,
        sys_implementation_name=sys.implementation.name,
        sys_path=sys.path,
        sys_platform=sys.platform,
        sys_prefix=sys.prefix,
        sys_version=sys.version,
        sys_version_info=list(sys.version_info),

        platform_architecture=list(platform.architecture()),
        platform_machine=platform.machine(),
        platform_platform=platform.platform(),
        platform_processor=platform.processor(),
        platform_system=platform.system(),
        platform_release=platform.release(),
        platform_version=platform.version(),

        site_userbase=site.getuserbase(),

        os_cwd=os.getcwd(),
        os_gid=os.getgid(),
        os_loadavg=list(os.getloadavg()),
        os_login=os_login,
        os_pgrp=os.getpgrp(),
        os_pid=os.getpid(),
        os_ppid=os.getppid(),
        os_uid=os_uid,

        pw_name=pw.pw_name,
        pw_uid=pw.pw_uid,
        pw_gid=pw.pw_gid,
        pw_gecos=pw.pw_gecos,
        pw_dir=pw.pw_dir,
        pw_shell=pw.pw_shell,

        env_path=os.environ.get('PATH'),
    )


##


class PyremoteBootstrapDriver:
    def __init__(self, main_src: str) -> None:
        super().__init__()

        self._main_src = main_src
        self._main_z = zlib.compress(main_src.encode('utf-8'))

    #

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

    def gen(self) -> ta.Generator[ta.Union[Read, Write], ta.Optional[bytes], Result]:
        # Read first ack
        yield from self._expect(_PYREMOTE_BOOTSTRAP_ACK0)

        # Read pid
        d = yield from self._read(8)
        pid = struct.unpack('<Q', d)[0]

        # Write main src
        yield from self._write(struct.pack('<I', len(self._main_z)))
        yield from self._write(self._main_z)

        # Read second and third ack
        yield from self._expect(_PYREMOTE_BOOTSTRAP_ACK1)
        yield from self._expect(_PYREMOTE_BOOTSTRAP_ACK2)

        # Read env info
        d = yield from self._read(4)
        env_info_json_len = struct.unpack('<I', d)[0]
        d = yield from self._read(env_info_json_len)
        env_info_json = d.decode('utf-8')
        env_info = PyremoteEnvInfo(**json.loads(env_info_json))

        # Read fourth ack
        yield from self._expect(_PYREMOTE_BOOTSTRAP_ACK3)

        # Return
        return self.Result(
            pid=pid,
            env_info=env_info,
        )

    def _read(self, sz: int) -> ta.Generator[Read, bytes, bytes]:
        d = yield self.Read(sz)
        if not isinstance(d, bytes):
            raise self.ProtocolError(f'Expected bytes after read, got {d!r}')
        if len(d) != sz:
            raise self.ProtocolError(f'Read {len(d)} bytes, expected {sz}')
        return d

    def _expect(self, e: bytes) -> ta.Generator[Read, bytes, None]:
        d = yield from self._read(len(e))
        if d != e:
            raise self.ProtocolError(f'Read {d!r}, expected {e!r}')

    def _write(self, d: bytes) -> ta.Generator[Write, ta.Optional[bytes], None]:
        i = yield self.Write(d)
        if i is not None:
            raise self.ProtocolError('Unexpected input after write')

    #

    def run(self, stdin: ta.IO, stdout: ta.IO) -> Result:
        gen = self.gen()

        gi: ta.Optional[bytes] = None
        while True:
            try:
                if gi is not None:
                    go = gen.send(gi)
                else:
                    go = next(gen)
            except StopIteration as e:
                return e.value

            if isinstance(go, self.Read):
                gi = stdout.read(go.sz)
            elif isinstance(go, self.Write):
                gi = None
                stdin.write(go.d)
                stdin.flush()
            else:
                raise TypeError(go)


##


@dc.dataclass(frozen=True)
class PyremotePayloadRuntime:
    input: ta.BinaryIO
    main_src: str
    env_info: PyremoteEnvInfo


def pyremote_bootstrap_finalize() -> PyremotePayloadRuntime:
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

    # Write env info
    env_info = _get_pyremote_env_info()
    env_info_json = json.dumps(dc.asdict(env_info), indent=None, separators=(',', ':'))  # noqa
    os.write(1, struct.pack('<I', len(env_info_json)))
    os.write(1, env_info_json.encode('utf-8'))

    # Write fourth ack
    os.write(1, _PYREMOTE_BOOTSTRAP_ACK3)

    # Return
    return PyremotePayloadRuntime(
        input=os.fdopen(_PYREMOTE_BOOTSTRAP_COMM_FD, 'rb', 0),
        main_src=main_src,
        env_info=env_info,
    )
