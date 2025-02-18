# ruff: noqa: UP006 UP007
# @omlish-lite
import dataclasses as dc
import typing as ta


NameAliasesManifestT = ta.TypeVar('NameAliasesManifestT', bound='NameAliasesManifest')


##


@dc.dataclass(frozen=True)
class ModAttrManifest:
    mod_name: str
    attr_name: str

    def load(self) -> ta.Any:
        importlib = __import__('importlib')
        mod = importlib.import_module(self.mod_name)
        return getattr(mod, self.attr_name)


##


@dc.dataclass(frozen=True)
class NameAliasesManifest:
    name: str
    aliases: ta.Optional[ta.Collection[str]] = None

    @classmethod
    def build_name_dict(cls, objs: ta.Iterable[NameAliasesManifestT]) -> ta.Dict[str, NameAliasesManifestT]:
        dct: ta.Dict[str, NameAliasesManifestT] = {}
        for o in objs:
            for n in (o.name, *(o.aliases or ())):
                if n in dct:
                    raise KeyError(n)
                dct[n] = o
        return dct
