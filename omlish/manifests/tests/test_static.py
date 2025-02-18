import abc
import dataclasses as dc  # Intentionally importing stdlib dataclasses to ensure interop

from ..base import ModAttrManifest
from ..base import NameAliasesManifest
from ..static import StaticModAttrManifest


@dc.dataclass(frozen=True)
class MyManifest(NameAliasesManifest, ModAttrManifest):
    pass


class StaticMyManifest(StaticModAttrManifest, MyManifest, abc.ABC):
    pass


class _MY_MANIFEST(StaticMyManifest):  # noqa
    attr_name = 'FOO_COUNT'
    name = 'foo'


def test_manifest():
    print(_MY_MANIFEST())
    assert _MY_MANIFEST.mod_name == __name__
