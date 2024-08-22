"""
Basically this: https://mitogen.networkgenomics.com/howitworks.html
"""
import base64
import inspect
import os
import sys
import textwrap
import typing as ta
import zlib


##


_BOOTSTRAP_COMM_FD = 100
_BOOTSTRAP_SRC_FD = 101

_BOOTSTRAP_CHILD_PID_VAR = '_PYR_CPID'
_BOOTSTRAP_ARGV0_VAR = '_PYR_ARGV0'

BOOTSTRAP_ACK0 = b'OPYR000\n'
BOOTSTRAP_ACK1 = b'OPYR001\n'

_BOOTSTRAP_PROC_TITLE_FMT = '(pyremote:%s)'

_BOOTSTRAP_IMPORTS = [
    'base64',
    'os',
    'sys',
    'zlib',
]


def _bootstrap_main(context_name: str, main_z_len: int) -> None:
    # Two copies of main src to be sent to parent
    r0, w0 = os.pipe()
    r1, w1 = os.pipe()

    if (cp := os.fork()):
        # Parent process

        # Dup original stdin to comm_fd for use as comm channel
        os.dup2(0, _BOOTSTRAP_COMM_FD)

        # Overwrite stdin (fed to python repl) with first copy of src
        os.dup2(r0, 0)

        # Dup second copy of src to src_fd to recover after launch
        os.dup2(r1, _BOOTSTRAP_SRC_FD)

        # Close remaining fd's
        for f in [r0, w0, r1, w1]:
            os.close(f)

        # Save child pid to close after relaunch
        os.environ[_BOOTSTRAP_CHILD_PID_VAR] = str(cp)

        # Save original argv0
        os.environ[_BOOTSTRAP_ARGV0_VAR] = sys.executable

        # Start repl reading stdin from r0
        os.execl(sys.executable, sys.executable + (_BOOTSTRAP_PROC_TITLE_FMT % (context_name,)))

    else:
        # Child process

        # Write first ack
        os.write(1, BOOTSTRAP_ACK0)

        # Read main src from stdin
        main_src = zlib.decompress(os.fdopen(0, 'rb').read(main_z_len))

        # Write both copies of main src
        for w in [w0, w1]:
            fp = os.fdopen(w, 'wb', 0)
            fp.write(main_src)
            fp.close()

        # Write second ack
        os.write(1, BOOTSTRAP_ACK1)

        sys.exit(0)


#


def bootstrap_payload(context_name: str, main_z_len: int) -> str:
    bs_src = textwrap.dedent(inspect.getsource(_bootstrap_main))

    for gl in [
        '_BOOTSTRAP_COMM_FD',
        '_BOOTSTRAP_SRC_FD',

        '_BOOTSTRAP_CHILD_PID_VAR',
        '_BOOTSTRAP_ARGV0_VAR',

        'BOOTSTRAP_ACK0',
        'BOOTSTRAP_ACK1',

        '_BOOTSTRAP_PROC_TITLE_FMT',
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
        f'import {", ".join(_BOOTSTRAP_IMPORTS)}',
        f'exec(zlib.decompress(base64.decodebytes({bs_z64!r})))',
        f'_bootstrap_main({context_name!r}, {main_z_len})',
    ]

    cmd = '; '.join(stmts)
    return cmd


#


class PostBoostrap(ta.NamedTuple):
    input: ta.BinaryIO
    main_src: str


def post_boostrap() -> PostBoostrap:
    # Restore original argv0
    sys.executable = os.environ.pop(_BOOTSTRAP_ARGV0_VAR)

    # Reap boostrap child
    os.waitpid(int(os.environ.pop(_BOOTSTRAP_CHILD_PID_VAR)), 0)

    # Read second copy of main src
    r1 = os.fdopen(_BOOTSTRAP_SRC_FD, 'rb', 0)
    main_src = r1.read().decode('utf-8')
    r1.close()

    return PostBoostrap(
        input=os.fdopen(_BOOTSTRAP_COMM_FD, 'rb', 0),
        main_src=main_src,
    )
