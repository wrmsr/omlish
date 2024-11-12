import dataclasses as dc
import json
import os.path
import plistlib
import re
import shutil
import subprocess
import sys
import typing as ta

from .. import check
from .. import lang


if ta.TYPE_CHECKING:
    docker = lang.proxy_import('..docker')
else:
    from .. import docker


##


PYCHARM_HOSTED_ENV_VAR = 'PYCHARM_HOSTED'


def is_pycharm_hosted() -> bool:
    return PYCHARM_HOSTED_ENV_VAR in os.environ


##


DARWIN_PYCHARM_HOME = '/Applications/PyCharm.app'


def read_darwin_pycharm_info_plist() -> ta.Mapping[str, ta.Any] | None:
    plist_file = os.path.join(DARWIN_PYCHARM_HOME, 'Contents', 'Info.plist')
    if not os.path.isfile(plist_file):
        return None

    with open(plist_file, 'rb') as f:
        root = plistlib.load(f)

    return root


#


UBUNTU_PYCHARM_HOME = '/snap/pycharm-professional/current'


def read_ubuntu_pycharm_product_info() -> ta.Mapping[str, ta.Any] | None:
    json_file = os.path.join(UBUNTU_PYCHARM_HOME, 'product-info.json')
    if not os.path.isfile(json_file):
        return None

    with open(json_file) as f:
        root = json.load(f)

    return root


#


@lang.cached_function
def get_pycharm_version() -> str | None:
    if sys.platform == 'darwin':
        plist = read_darwin_pycharm_info_plist()
        if plist is None:
            return None

        ver = check.non_empty_str(plist['CFBundleVersion'])
        check.state(ver.startswith('PY-'))
        return ver[3:]

    elif sys.platform == 'linux':
        if shutil.which('lsb_release') is not None:
            lsb_id = subprocess.check_output(['lsb_release', '-is']).decode().strip()
            if lsb_id == 'Ubuntu':
                pi = read_ubuntu_pycharm_product_info()
                if pi is not None:
                    ver = check.non_empty_str(pi['buildNumber'])
                    return ver

        return None

    else:
        return None


##


def _import_pydevd_pycharm(*, version: str | None = None) -> ta.Any:
    if (
            'pydevd_pycharm' in sys.modules or
            (version is None and lang.can_import('pydevd_pycharm'))
    ):
        # Can't unload, nothing we can do
        import pydevd_pycharm  # noqa
        return pydevd_pycharm

    proc = subprocess.run([  # noqa
        sys.executable,
        '-m', 'pip',
        'show',
        'pydevd_pycharm',
    ], stdout=subprocess.PIPE)

    if not proc.returncode:
        info = {
            k: v.strip()
            for l in proc.stdout.decode().splitlines()
            if (s := l.strip())
            for k, _, v in [s.partition(':')]
        }

        installed_version = info['Version']
        if installed_version == version:
            import pydevd_pycharm  # noqa
            return pydevd_pycharm

        subprocess.check_call([
            sys.executable,
            '-m', 'pip',
            'uninstall', '-y',
            'pydevd_pycharm',
        ])

    subprocess.check_call([
        sys.executable,
        '-m', 'pip',
        'install',
        'pydevd_pycharm' + (f'=={version}' if version is not None else ''),
    ])

    import pydevd_pycharm  # noqa
    return pydevd_pycharm


@dc.dataclass(frozen=True)
class PycharmRemoteDebugger:
    host: str | None
    port: int
    version: str | None = None

    def __str__(self) -> str:
        return ''.join([
            f'@{self.version}:' if self.version is not None else '',
            f'{self.host}:' if self.host is not None else '',
            str(self.port),
        ])

    @classmethod
    def parse(cls, s: str) -> 'PycharmRemoteDebugger':
        if (m := re.fullmatch(r'(@(?P<version>[^:]+):)?((?P<host>[^:]+):)?(?P<port>\d+)', s)) is None:
            raise ValueError(s)
        gd = m.groupdict()
        return cls(
            host=gd.get('host'),
            port=int(gd['port']),
            version=gd.get('version'),
        )


def pycharm_remote_debugger_attach(prd: PycharmRemoteDebugger) -> None:
    host = prd.host
    if host is None:
        if (
                sys.platform == 'linux' and
                docker.is_likely_in_docker() and
                docker.get_docker_host_platform() == 'darwin'
        ):
            host = docker.DOCKER_FOR_MAC_HOSTNAME
        else:
            host = 'localhost'

    version = prd.version
    if version is None and host in ('localhost', '127.0.0.1'):
        version = get_pycharm_version()

    if ta.TYPE_CHECKING:
        import pydevd_pycharm  # noqa
    else:
        pydevd_pycharm = _import_pydevd_pycharm(version=version)

    pydevd_pycharm.settrace(
        host,
        port=prd.port,
        stdoutToServer=True,
        stderrToServer=True,
    )
