import os.path
import plistlib
import subprocess
import sys
import typing as ta

from .. import check
from .. import lang


if ta.TYPE_CHECKING:
    docker = lang.proxy_import('omlish.docker')
else:
    from omlish import docker


##


PYCHARM_HOSTED_ENV_VAR = 'PYCHARM_HOSTED'


def is_pycharm_hosted() -> bool:
    return PYCHARM_HOSTED_ENV_VAR in os.environ


##


PYCHARM_HOME = '/Applications/PyCharm.app'


def read_pycharm_info_plist() -> ta.Mapping[str, ta.Any] | None:
    plist_file = os.path.join(PYCHARM_HOME, 'Contents', 'Info.plist')
    if not os.path.isfile(plist_file):
        return None

    with open(plist_file, 'rb') as f:
        root = plistlib.load(f)

    return root


@lang.cached_function
def get_pycharm_version() -> str | None:
    plist = read_pycharm_info_plist()
    if plist is None:
        return None

    ver = check.non_empty_str(plist['CFBundleVersion'])
    check.state(ver.startswith('PY-'))
    return ver[3:]


##


def pycharm_remote_debugger_attach(
        host: str | None,
        port: int,
        *,
        version: str | None = None,
) -> None:
    # if version is None:
    #     version = get_pycharm_version()
    # check.non_empty_str(version)

    if host is None:
        if sys.platform == 'linux' and docker.is_likely_in_docker():
            host = docker.DOCKER_FOR_MAC_HOSTNAME
        else:
            host = 'localhost'

    try:
        import pydevd_pycharm  # noqa
    except ImportError:
        subprocess.check_call([
            sys.executable,
            '-mpip',
            'install',
            'pydevd-pycharm' + (f'~={version}' if version is not None else ''),
        ])

    import pydevd_pycharm  # noqa
    pydevd_pycharm.settrace(
        host,
        port=port,
        stdoutToServer=True,
        stderrToServer=True,
    )
