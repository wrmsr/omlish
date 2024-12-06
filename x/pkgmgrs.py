import abc
import dataclasses as dc
import json
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
    def install(self, *packages: SystemPackageOrStr) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def query(self, *packages: SystemPackageOrStr) -> ta.Mapping[str, SystemPackage]:
        raise NotImplementedError


class BrewSystemPackageManager(SystemPackageManager):
    def update(self) -> None:
        subprocess.check_call(['brew', 'update'])

    def install(self, *packages: SystemPackageOrStr) -> None:
        raise NotImplementedError

    def query(self, *packages: SystemPackageOrStr) -> ta.Mapping[str, SystemPackage]:
        pns = [p if isinstance(p, str) else p.name for p in packages]
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
    pass


class YumSystemPackageManager(SystemPackageManager):
    pass


def _main() -> None:
    spm = BrewSystemPackageManager()
    # spm.update()
    print(spm.query('jq', 'gcc', 'gfortran'))


if __name__ == '__main__':
    _main()
