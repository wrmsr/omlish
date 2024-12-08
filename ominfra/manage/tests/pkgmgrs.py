# ruff: noqa: UP006 UP007
"""
TODO:
 - yum/rpm
"""
import abc
import dataclasses as dc
import json
import os
import subprocess
import typing as ta


SystemPackageOrStr = ta.Union['SystemPackage', str]


@dc.dataclass(frozen=True)
class SystemPackage:
    name: str
    version: ta.Optional[str] = None


class SystemPackageManager(abc.ABC):
    @abc.abstractmethod
    def update(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def upgrade(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def install(self, *packages: SystemPackageOrStr) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def query(self, *packages: SystemPackageOrStr) -> ta.Mapping[str, SystemPackage]:
        raise NotImplementedError


class BrewSystemPackageManager(SystemPackageManager):
    def update(self) -> None:
        subprocess.check_call(['brew', 'update'])

    def upgrade(self) -> None:
        subprocess.check_call(['brew', 'upgrade'])

    def install(self, *packages: SystemPackageOrStr) -> None:
        es: ta.List[str] = []
        for p in packages:
            if isinstance(p, SystemPackage):
                es.append(p.name + (f'@{p.version}' if p.version is not None else ''))
            else:
                es.append(p)
        subprocess.check_call(['brew', 'install', *es])

    def query(self, *packages: SystemPackageOrStr) -> ta.Mapping[str, SystemPackage]:
        pns = [p.name if isinstance(p, SystemPackage) else p for p in packages]
        o = subprocess.check_output(['brew', 'info', '--json', *pns])
        j = json.loads(o.decode())
        d: ta.Dict[str, SystemPackage] = {}
        for e in j:
            if not e['installed']:
                continue
            d[e['name']] = SystemPackage(
                name=e['name'],
                version=e['installed'][0]['version'],
            )
        return d


class AptSystemPackageManager(SystemPackageManager):
    _APT_ENV: ta.ClassVar[ta.Mapping[str, str]] = {
        'DEBIAN_FRONTEND': 'noninteractive',
    }

    def update(self) -> None:
        subprocess.check_call(['apt', 'update'], env={**os.environ, **self._APT_ENV})

    def upgrade(self) -> None:
        subprocess.check_call(['apt', 'upgrade', '-y'], env={**os.environ, **self._APT_ENV})

    def install(self, *packages: SystemPackageOrStr) -> None:
        pns = [p.name if isinstance(p, SystemPackage) else p for p in packages]  # FIXME: versions
        subprocess.check_call(['apt', 'upgrade', '-y', *pns], env={**os.environ, **self._APT_ENV})

    def query(self, *packages: SystemPackageOrStr) -> ta.Mapping[str, SystemPackage]:
        pns = [p.name if isinstance(p, SystemPackage) else p for p in packages]
        cmd = ['dpkg-query', '-W', '-f=${Package}=${Version}\n', *pns]
        res = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )
        d: ta.Dict[str, SystemPackage] = {}
        for l in res.stdout.strip().splitlines():
            n, v = l.split('=', 1)
            d[n] = SystemPackage(
                name=n,
                version=v,
            )
        return d


def _main() -> None:
    spm = BrewSystemPackageManager()
    print(spm.query('jq', 'gcc', 'gfortran'))
    spm.install('cowsay')


if __name__ == '__main__':
    _main()
