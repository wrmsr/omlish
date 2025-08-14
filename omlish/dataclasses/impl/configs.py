import dataclasses as dc
import importlib.resources
import json
import typing as ta


##


PACKAGE_CONFIG_FILE_NAME = '.dataclasses.json'


@dc.dataclass(frozen=True, kw_only=True)
class PackageConfig:
    codegen: bool = False

    def __init_subclass__(cls, **kwargs):
        raise TypeError

    @classmethod
    def loads(cls, s: str) -> 'PackageConfig':
        return cls(**json.loads(s))

    def dumps(self) -> str:
        return json.dumps(dc.asdict(self), indent=2)


DEFAULT_PACKAGE_CONFIG = PackageConfig()


##


class PackageConfigCache:
    def __init__(self) -> None:
        super().__init__()

        self._dct: dict[str, PackageConfig | None] = {}

    @ta.overload
    def get(self, pkg: str, default: PackageConfig) -> PackageConfig:
        ...

    @ta.overload
    def get(self, pkg: str, default: PackageConfig | None = None) -> PackageConfig | None:
        ...

    def get(self, pkg, default=None):
        try:
            return self._dct[pkg]
        except KeyError:
            pass

        try:
            s = importlib.resources.read_text(pkg, PACKAGE_CONFIG_FILE_NAME)
        except FileNotFoundError:
            self._dct[pkg] = None
        else:
            c = PackageConfig.loads(s)
            self._dct[pkg] = c
            return c

        if '.' not in pkg:
            return default

        return self.get(pkg.rpartition('.')[0], default)


PACKAGE_CONFIG_CACHE = PackageConfigCache()
