"""
TODO:
 - better support anonymous / weakref'd / unlaoded modules / etc.
  - anonymous=False on class spec?
"""
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


@ta.final
class PackageConfigCache:
    def __init__(self) -> None:
        super().__init__()

        self._lock = threading.Lock()
        self._root = PackageConfigCache._Node('', None)
        self._nodes: dict[str, PackageConfigCache._Node] = {}

    @ta.final
    class _Node:
        def __init__(self, pkg: str, cfg: PackageConfig | None) -> None:
            self.pkg = pkg
            self.cfg = cfg

            self.children: dict[str, PackageConfigCache._Node] = {}

        def __repr__(self) -> str:
            return f'{self.__class__.__name__}(pkg={self.pkg!r}, cfg={self.cfg!r})'

    def _navigate(self, *parts: str) -> _Node:
        node = self._root
        for i, p in enumerate(parts):
            if (child := node.children.get(p)) is None:
                child_pkg = '.'.join(parts[:i + 1])
                check.not_in(child_pkg, self._nodes)
                child = node.children[p] = self._nodes[child_pkg] = PackageConfigCache._Node(child_pkg, node.cfg)
            node = child
        return node

    def put(self, pkg: str, cfg: PackageConfig) -> None:
        check.non_empty_str(pkg)
        with self._lock:
            check.not_in(pkg, self._nodes)
            parts = pkg.split('.')
            parent = self._navigate(*parts[:-1])
            check.not_in(parts[-1], parent.children)
            parent.children[parts[-1]] = self._nodes[pkg] = PackageConfigCache._Node(pkg, cfg)

    def get(self, pkg: str) -> PackageConfig | None:
        if not pkg:
            return None

        try:
            node = self._nodes[pkg]
        except KeyError:
            pass
        else:
            return node.cfg

        # Flimsy - if no config anywhere for root package then don't cache. Want to support unlimited anonymous modules
        # which may be unloaded without polluting cache forever.
        parts = pkg.split('.')
        if parts[0] not in self._root.children:
            return None

        with self._lock:
            try:
                node = self._nodes[pkg]
            except KeyError:
                pass
            else:
                return node.cfg

            node = self._navigate(*pkg.split('.'))
            return node.cfg


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
