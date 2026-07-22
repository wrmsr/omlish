# ruff: noqa: UP006 UP007 UP045
import dataclasses as dc
import typing as ta


##


DEFAULT_PYCHARM_VERSION = '252.26199.168'


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

    # The function source must not pass through dedent with the template - its body lines have less indentation than
    # the template's, which would leave the def line indented relative to its body.
    return '\n'.join([
        inspect.getsource(pycharm_debug_connect),
        textwrap.dedent(f"""
            pycharm_debug_connect(PycharmRemoteDebug(
                {prd.port!r},
                host={prd.host!r},
                install_version={prd.install_version!r},
            ))
        """),
    ])
