# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import dataclasses as dc
import typing as ta


NameAliasesManifestT = ta.TypeVar('NameAliasesManifestT', bound='NameAliasesManifest')


##


@dc.dataclass(frozen=True)
class ModAttrManifest:
    module: str
    attr: str

    def resolve(self) -> ta.Any:
        import importlib  # noqa

        mod = importlib.import_module(self.module)
        return getattr(mod, self.attr)


##


@dc.dataclass(frozen=True)
class NameAliasesManifest:
    name: str
    aliases: ta.Optional[ta.Sequence[str]] = None

    @classmethod
    def build_name_dict(cls, objs: ta.Iterable[NameAliasesManifestT]) -> ta.Dict[str, NameAliasesManifestT]:
        dct: ta.Dict[str, NameAliasesManifestT] = {}
        for o in objs:
            for n in (o.name, *(o.aliases or ())):
                if n in dct:
                    raise KeyError(n)
                dct[n] = o
        return dct
