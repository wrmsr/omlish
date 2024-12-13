# ruff: noqa: UP006 UP007
"""
TODO:
 - yum/rpm
"""
import abc
import dataclasses as dc
import json
import os
import typing as ta

from omlish.asyncs.asyncio.subprocesses import asyncio_subprocesses
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
        await asyncio_subprocesses.check_call('brew', 'update')

    async def upgrade(self) -> None:
        await asyncio_subprocesses.check_call('brew', 'upgrade')

    async def install(self, *packages: SystemPackageOrStr) -> None:
        es: ta.List[str] = []
        for p in packages:
            if isinstance(p, SystemPackage):
                es.append(p.name + (f'@{p.version}' if p.version is not None else ''))
            else:
                es.append(p)
        await asyncio_subprocesses.check_call('brew', 'install', *es)

    async def query(self, *packages: SystemPackageOrStr) -> ta.Mapping[str, SystemPackage]:
        pns = [p.name if isinstance(p, SystemPackage) else p for p in packages]
        o = await asyncio_subprocesses.check_output('brew', 'info', '--json', *pns)
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
        await asyncio_subprocesses.check_call('sudo', 'apt', 'update', env={**os.environ, **self._APT_ENV})

    async def upgrade(self) -> None:
        await asyncio_subprocesses.check_call('sudo', 'apt', 'upgrade', '-y', env={**os.environ, **self._APT_ENV})

    async def install(self, *packages: SystemPackageOrStr) -> None:
        pns = [p.name if isinstance(p, SystemPackage) else p for p in packages]  # FIXME: versions
        await asyncio_subprocesses.check_call('sudo', 'apt', 'install', '-y', *pns, env={**os.environ, **self._APT_ENV})

    async def query(self, *packages: SystemPackageOrStr) -> ta.Mapping[str, SystemPackage]:
        pns = [p.name if isinstance(p, SystemPackage) else p for p in packages]
        out = await asyncio_subprocesses.run(
            'dpkg-query', '-W', '-f=${Package}=${Version}\n', *pns,
            capture_output=True,
            check=False,
        )
        d: ta.Dict[str, SystemPackage] = {}
        for l in check.not_none(out.stdout).decode('utf-8').strip().splitlines():
            n, v = l.split('=', 1)
            d[n] = SystemPackage(
                name=n,
                version=v,
            )
        return d


class YumSystemPackageManager(SystemPackageManager):
    async def update(self) -> None:
        await asyncio_subprocesses.check_call('sudo', 'yum', 'check-update')

    async def upgrade(self) -> None:
        await asyncio_subprocesses.check_call('sudo', 'yum', 'update')

    async def install(self, *packages: SystemPackageOrStr) -> None:
        pns = [p.name if isinstance(p, SystemPackage) else p for p in packages]  # FIXME: versions
        await asyncio_subprocesses.check_call('sudo', 'yum', 'install', *pns)

    async def query(self, *packages: SystemPackageOrStr) -> ta.Mapping[str, SystemPackage]:
        pns = [p.name if isinstance(p, SystemPackage) else p for p in packages]
        d: ta.Dict[str, SystemPackage] = {}
        for pn in pns:
            out = await asyncio_subprocesses.run(
                'rpm', '-q', pn,
                capture_output=True,
            )
            if not out.proc.returncode:
                d[pn] = SystemPackage(
                    pn,
                    check.not_none(out.stdout).decode().strip(),
                )
        return d
