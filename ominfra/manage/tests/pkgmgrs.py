# ruff: noqa: UP006 UP007
"""
TODO:
 - yum/rpm
"""
import abc
import asyncio
import dataclasses as dc
import json
import os
import typing as ta

from omlish.lite.asyncio.subprocesses import asyncio_subprocess_check_call
from omlish.lite.asyncio.subprocesses import asyncio_subprocess_check_output
from omlish.lite.asyncio.subprocesses import asyncio_subprocess_run
from omlish.lite.check import check


SystemPackageOrStr = ta.Union['SystemPackage', str]


@dc.dataclass(frozen=True)
class SystemPackage:
    name: str
    version: ta.Optional[str] = None


class SystemPackageManager(abc.ABC):
    @abc.abstractmethod
    def update(self) -> ta.Awaitable[None]:
        raise NotImplementedError

    @abc.abstractmethod
    def upgrade(self) -> ta.Awaitable[None]:
        raise NotImplementedError

    @abc.abstractmethod
    def install(self, *packages: SystemPackageOrStr) -> ta.Awaitable[None]:
        raise NotImplementedError

    @abc.abstractmethod
    def query(self, *packages: SystemPackageOrStr) -> ta.Awaitable[ta.Mapping[str, SystemPackage]]:
        raise NotImplementedError


class BrewSystemPackageManager(SystemPackageManager):
    async def update(self) -> None:
        await asyncio_subprocess_check_call('brew', 'update')

    async def upgrade(self) -> None:
        await asyncio_subprocess_check_call('brew', 'upgrade')

    async def install(self, *packages: SystemPackageOrStr) -> None:
        es: ta.List[str] = []
        for p in packages:
            if isinstance(p, SystemPackage):
                es.append(p.name + (f'@{p.version}' if p.version is not None else ''))
            else:
                es.append(p)
        await asyncio_subprocess_check_call('brew', 'install', *es)

    async def query(self, *packages: SystemPackageOrStr) -> ta.Mapping[str, SystemPackage]:
        pns = [p.name if isinstance(p, SystemPackage) else p for p in packages]
        o = await asyncio_subprocess_check_output('brew', 'info', '--json', *pns)
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

    async def update(self) -> None:
        await asyncio_subprocess_check_call('apt', 'update', env={**os.environ, **self._APT_ENV})

    async def upgrade(self) -> None:
        await asyncio_subprocess_check_call('apt', 'upgrade', '-y', env={**os.environ, **self._APT_ENV})

    async def install(self, *packages: SystemPackageOrStr) -> None:
        pns = [p.name if isinstance(p, SystemPackage) else p for p in packages]  # FIXME: versions
        await asyncio_subprocess_check_call('apt', 'upgrade', '-y', *pns, env={**os.environ, **self._APT_ENV})

    async def query(self, *packages: SystemPackageOrStr) -> ta.Mapping[str, SystemPackage]:
        pns = [p.name if isinstance(p, SystemPackage) else p for p in packages]
        cmd = ['dpkg-query', '-W', '-f=${Package}=${Version}\n', *pns]
        stdout, stderr = await asyncio_subprocess_run(
            *cmd,
            capture_output=True,
            check=False,
        )
        d: ta.Dict[str, SystemPackage] = {}
        for l in check.not_none(stdout).decode('utf-8').strip().splitlines():
            n, v = l.split('=', 1)
            d[n] = SystemPackage(
                name=n,
                version=v,
            )
        return d


async def _async_main() -> None:
    spm = BrewSystemPackageManager()
    print(await spm.query('jq', 'gcc', 'gfortran'))
    await spm.install('cowsay')


if __name__ == '__main__':
    asyncio.run(_async_main())
