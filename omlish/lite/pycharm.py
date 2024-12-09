# ruff: noqa: UP006 UP007
import dataclasses as dc
import typing as ta


DEFAULT_PYCHARM_VERSION = '242.23726.102'


@dc.dataclass(frozen=True)
class PycharmRemoteDebug:
    port: int
    host: ta.Optional[str] = 'localhost'
    install_version: ta.Optional[str] = DEFAULT_PYCHARM_VERSION


def pycharm_debug_connect(prd: PycharmRemoteDebug) -> None:
    if prd.install_version is not None:
        import subprocess
        import sys
        subprocess.check_call([
            sys.executable,
            '-mpip',
            'install',
            f'pydevd-pycharm~={prd.install_version}',
        ])

    pydevd_pycharm = __import__('pydevd_pycharm')  # noqa
    pydevd_pycharm.settrace(
        prd.host,
        port=prd.port,
        stdoutToServer=True,
        stderrToServer=True,
    )


def pycharm_debug_preamble(prd: PycharmRemoteDebug) -> str:
    import inspect
    import textwrap
    return textwrap.dedent(f"""
        {inspect.getsource(pycharm_debug_connect)}

        pycharm_debug_connect(PycharmRemoteDebug(
            {prd.port!r},
            host={prd.host!r},
            install_version={prd.install_version!r},
        ))
    """)
