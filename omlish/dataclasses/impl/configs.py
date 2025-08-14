import dataclasses as dc
import json


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


##


class PackageConfigCache:
    def __init__(self) -> None:
        super().__init__()

        self._dct: dict[str, PackageConfig] = {}

    def get(self, pkg: str) -> PackageConfig | None:
        try:
            return self._dct[pkg]
        except KeyError:
            pass

        raise NotImplementedError


PACKAGE_CONFIG_CACHE = PackageConfigCache()
