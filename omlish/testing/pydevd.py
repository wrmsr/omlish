"""
A small but likely growing collection of (completely optional) tools to make pydevd (PyCharm's, among other python
IDE's, debugger) do hard things. Originally explored and added to get spark jvm python subprocesses to connect back to
an already-debugging PyCharm instance to debug PySpark jobs.

TODO:
 - https://www.jetbrains.com/help/pycharm/remote-debugging-with-product.html#
 - PyCharm.app/Contents/plugins/python/helpers/pydev/_pydevd_bundle/pydevd_constants.py -> USE_LOW_IMPACT_MONITORING

==

https://www.jetbrains.com/help/pycharm/remote-debugging-with-product.html#remote-debug-config ->

pycharm_port = 43251
pycharm_version = '241.18034.82'
buf = textwrap.dedent(f'''
    import subprocess
    import sys
    subprocess.check_call([sys.executable, '-mpip', 'install', f'pydevd-pycharm~={pycharm_version}'])

    import pydevd_pycharm  # noqa
    pydevd_pycharm.settrace(
        'docker.for.mac.localhost',
         port={pycharm_port},
          stdoutToServer=True,
           stderrToServer=True,
       )
''') + '\n' * 2 + buf
"""
import json
import os
import sys
import tempfile
import textwrap
import types
import typing as ta

from .. import check
from .. import lang


ALLOW_DEBUGGER_CALLS = False


DEBUGGER_CALL_PACKAGES = {
    '_pydevd_bundle',
}


def is_debugger_call(hoist: int = 0, walk: int = 2) -> bool:
    frame: ta.Optional[types.FrameType] = sys._getframe(2 + hoist)  # noqa
    for _ in range(walk):
        if frame is None:
            break
        package = frame.f_globals.get('__package__')
        if package in DEBUGGER_CALL_PACKAGES:
            return True
        frame = frame.f_back
    return False


class DebuggerCallForbiddenError(Exception):
    pass


def forbid_debugger_call(hoist: int = 0) -> None:
    # FIXME: only reentrant?
    if not ALLOW_DEBUGGER_CALLS and is_debugger_call(hoist + 1):
        raise DebuggerCallForbiddenError


##


@lang.cached_function
def silence_subprocess_check() -> None:
    try:
        # /Applications/PyCharm.app/Contents/plugins/python/helpers/pydev/_pydev_bundle/pydev_monkey.py
        from _pydev_bundle import pydev_monkey  # noqa
    except ImportError:
        return

    new_tb = lang.proxy_import('traceback')
    new_tb.print_exc = lambda *a, **k: None  # type: ignore  # noqa
    pydev_monkey.traceback = new_tb


@lang.cached_function
def patch_for_trio_asyncio() -> None:
    """Fix for `trio a callable object was expected by call_soon(), got Task`"""

    try:
        import pydevd_nest_asyncio  # noqa
    except ImportError:
        return

    import trio_asyncio._base  # noqa

    def new_call_soon(self, callback, *args, **context):
        _, callback = pydevd_nest_asyncio._PydevdAsyncioUtils.try_to_get_internal_callback(callback)  # noqa
        return orig_call_soon(self, callback, *args, **context)

    orig_call_soon = trio_asyncio._base.BaseTrioEventLoop.call_soon  # noqa
    trio_asyncio._base.BaseTrioEventLoop.call_soon = new_call_soon  # noqa


##


@lang.cached_function
def _pydevd() -> types.ModuleType | None:
    try:
        return __import__('pydevd')
    except ImportError:
        return None


def is_present() -> bool:
    return _pydevd() is not None


def get_setup() -> dict | None:
    if is_present():
        return _pydevd().SetupHolder.setup
    else:
        return None


def is_running() -> bool:
    return get_setup() is not None


##


ARGS_ENV_VAR = 'PYDEVD_ARGS'


def get_args() -> list[str]:
    check.state(is_present())
    setup: ta.Mapping[ta.Any, ta.Any] = check.isinstance(get_setup(), dict)
    args = [_pydevd().__file__]

    for k in [
        'port',
        'vm_type',
        'client',
    ]:
        if v := setup[k]:
            args.extend(['--' + k, str(v)])

    for k in [
        'server',
        'multiproc',
        'multiprocess',
        'save-signatures',
        'save-threading',
        'save-asyncio',
        'print-in-debugger-startup',
        'cmd-line',
    ]:
        if setup[k]:
            args.append('--' + k)

    if setup['qt-support']:
        args.append('--qt-support=' + setup['qt-support'])

    return args


def save_args() -> None:
    if is_present():
        os.environ[ARGS_ENV_VAR] = json.dumps(get_args())


def maybe_reexec(
        *,
        file: str | None = None,
        module: str | None = None,
        silence: bool = False,
) -> None:
    if ARGS_ENV_VAR not in os.environ:
        return

    try:
        import pydevd  # noqa
    except ImportError:
        return

    if pydevd.SetupHolder.setup is not None:  # noqa
        return

    if module is not None:
        if file is not None:
            raise ValueError

        tmpdir = tempfile.mkdtemp()
        bootstrap_path = os.path.join(tmpdir, 'bootstrap.py')
        with open(bootstrap_path, 'w') as f:
            f.write(textwrap.dedent(f"""
            import sys
            old_paths = set(sys.path)
            for new_path in {sys.path!r}:
                if new_path not in old_paths:
                    sys.path.insert(0, new_path)

            import runpy
            runpy.run_module({module!r}, run_name='__main__')
            """))
        file = bootstrap_path

    elif file is None:
        raise ValueError

    args = [sys.executable]
    args.extend(json.loads(os.environ[ARGS_ENV_VAR]))
    args.extend(['--file', file])
    args.extend(sys.argv[1:])

    if silence:
        tmpdir = tempfile.mkdtemp()
        bootstrap_path = os.path.join(tmpdir, 'bootstrap.py')
        with open(bootstrap_path, 'w') as f:
            f.write(textwrap.dedent(f"""
            import sys
            old_paths = set(sys.path)
            for new_path in {sys.path!r}:
                if new_path not in old_paths:
                    sys.path.insert(0, new_path)

            _stderr_write = sys.stderr.write
            def stderr_write(*args, **kwargs):
                code = sys._getframe(1).f_code
                if code is not None and code.co_filename and code.co_filename.endswith('/pydev_log.py'):
                    return
                _stderr_write(*args, **kwargs)
            sys.stderr.write = stderr_write

            sys.argv = {args[1:]!r}
            import runpy
            runpy.run_path({args[1]!r}, run_name='__main__')
            """))
        args = [args[0], bootstrap_path]

    os.execvp(sys.executable, args)
