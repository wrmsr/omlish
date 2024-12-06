# ruff: noqa: UP007
import typing as ta


DEFAULT_PYCHARM_VERSION = '242.23726.102'


def pycharm_debug_connect(
        port: int,
        *,
        host: str = 'localhost',
        install_version: ta.Optional[str] = DEFAULT_PYCHARM_VERSION,
):
    if install_version is not None:
        import subprocess
        import sys
        subprocess.check_call([
            sys.executable,
            '-mpip',
            'install',
            f'pydevd-pycharm~={install_version}',
        ])

    pydevd_pycharm = __import__('pydevd_pycharm')  # noqa
    pydevd_pycharm.settrace(
        host,
        port=port,
        stdoutToServer=True,
        stderrToServer=True,
    )


def pycharm_debug_preamble(
        port: int,
        *,
        host: str = 'localhost',
        install_version: ta.Optional[str] = DEFAULT_PYCHARM_VERSION,
) -> str:
    import inspect
    import textwrap

    return textwrap.dedent(f"""
        {inspect.getsource(pycharm_debug_connect)}

        pycharm_debug_connect(
            {port},
            host={host!r},
            install_version={install_version!r},
        )
    """)
