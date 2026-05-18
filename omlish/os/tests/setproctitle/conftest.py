import os.path
import subprocess as sp
import sys

import pytest


skip_if_macos = pytest.mark.skipif(
    "sys.platform == 'darwin'", reason='skipping test on macOS',
)

skip_if_pypy = pytest.mark.skipif(
    "'__pypy__' in sys.builtin_module_names", reason='skipping test on pypy',
)

skip_if_no_proc_env = pytest.mark.skipif(
    "not os.path.exists('/proc/self/environ')",
    reason="'/proc/self/environ' not available",
)

skip_if_no_proc_cmdline = pytest.mark.skipif(
    "not os.path.exists('/proc/%s/cmdline' % os.getpid())",
    reason="'/proc/PID/cmdline' not available",
)

skip_if_no_proc_tasks = pytest.mark.skipif(
    "not os.path.exists('/proc/self/task')",
    reason="'/proc/self/task' not available",
)


@pytest.fixture
def tmp_pypath(monkeypatch, tmp_path):
    """return a tmp directory which has been added to the python path"""

    monkeypatch.setenv(
        'PYTHONPATH',
        str(tmp_path) + os.pathsep + os.environ.get('PYTHONPATH', ''),
    )
    return tmp_path


def run_script(script=None, args=None, executable=None, env=None):
    """
    run a script in a separate process.

    if the script completes successfully, return its ``stdout``, else fail the test.
    """

    if executable is None:
        executable = sys.executable

    cmdline = str(executable)
    if args:
        cmdline = cmdline + ' ' + args

    env = {
        **(env if env is not None else os.environ),
        'PYTHONPATH': ':'.join([
            os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')),
            *([pp] if (pp := os.environ.get('PYTHONPATH')) is not None else []),
        ]),
    }

    proc = sp.Popen(  # noqa
        cmdline,
        stdin=sp.PIPE,
        stdout=sp.PIPE,
        stderr=sp.PIPE,
        env=env,
        shell=True,
        close_fds=True,
    )

    out, err = proc.communicate(script and script.encode())
    if 0 != proc.returncode:
        if out:
            print(out.decode('utf8', 'replace'), file=sys.stdout)
        if err:
            print(err.decode('utf8', 'replace'), file=sys.stderr)
        pytest.fail('test script failed')

    # Py3 subprocess generates bytes strings.
    out = out.decode()

    return out
