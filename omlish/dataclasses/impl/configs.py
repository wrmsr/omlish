import dataclasses as dc
import threading
import typing as ta

from ... import check


##


@dc.dataclass(frozen=True, kw_only=True)
class PackageConfig:
    codegen: bool = False

    def __init_subclass__(cls, **kwargs):
        raise TypeError


DEFAULT_PACKAGE_CONFIG = PackageConfig()


##


class PackageConfigCache:
    def __init__(self) -> None:
        super().__init__()

        self._lock = threading.RLock()
        self._nodes: dict[str, PackageConfigCache._Node] = {}
        self._roots: dict[str, PackageConfigCache._Node] = {}
        self._cache: dict[str, PackageConfig] = {}

    @ta.final
    class _Node:
        def __init__(self, name: str, cfg: PackageConfig | None = None) -> None:
            self.name = name
            self.cfg = cfg

            self.children: dict[str, PackageConfigCache._Node] = {}

    def put(self, pkg: str, cfg: PackageConfig) -> None:
        with self._lock:
            check.not_in(pkg, self._nodes)
            parts = pkg.split('.')
            dct: dict[str, PackageConfigCache._Node] = self._roots
            for p in parts[:-1]:
                node = dct.get(p)
                if node is None:
                    node = dct[p] = PackageConfigCache._Node(p)
                dct = node.children
            name = parts[-1]
            check.not_in(name, dct)
            node = self._Node(name, cfg)
            dct[name] = node
            self._nodes[pkg] = node

    def get(self, pkg: str) -> PackageConfig | None:
        return None


PACKAGE_CONFIG_CACHE = PackageConfigCache()


##


def init_package(
        init_globals: ta.MutableMapping[str, ta.Any],
        *,
        codegen: bool = False,
) -> None:
    pkg = check.non_empty_str(init_globals['__package__'])
    if init_globals['__name__'] not in (pkg, '__main__'):
        raise NameError('Must call dataclasses.init_package from __init__')

    pkg_cfg = PackageConfig(
        codegen=codegen,
    )

    PACKAGE_CONFIG_CACHE.put(pkg, pkg_cfg)
