"""
NOTES:
 - DO want to be able to cram a model spec into a string, like a db conn str, for argparse
  - dbapi, standardize my own conn str?
   - it uses a url
 - mini language - ideally regexable
  - inline json?
 - engine:repo/model
 - at signs for aliases? where?
 - 'piping'?
 - service type
 - conversion to / generation of Config tv's
 - huggingface handle 'tag dir is a file containing a rev'
 - ** make them manifest-able, yaml-able **
"""
import abc
import typing as ta

from omlish import cached
from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish.algorithm.toposort import mut_toposort
from ommlds import minichain as mc

from ommlds.minichain.backends.strings.parsing import ParsedBackendString
from ommlds.minichain.backends.strings.parsing import parse_backend_string


##


def instantiate_backend_string(
        service_cls: ta.Any,
        ps: ParsedBackendString,
        *args: ta.Any,
        **kwargs: ta.Any,
) -> ta.Any:
    be_name: str
    be_cfg: ta.Sequence[mc.Config]

    be_name = check.not_none(ps.backend)
    be_cfg = [
        mc.ModelName(check.isinstance(ps.model, ParsedBackendString.NameModel).name),
    ]

    return mc.registry_new(
        service_cls,
        be_name,
        *be_cfg,
        *args,
        **kwargs,
    )


def test_instantiate_backend_strings():
    svc = instantiate_backend_string(
        'ChatChoicesService',
        parse_backend_string('anthropic:claude-3-7-sonnet-latest'),
        mc.ApiKey('abcd'),
    )
    print(svc)


##


class BackendStringInstantiator(lang.Abstract):
    @abc.abstractmethod
    def instantiate_backend_string(self, bs: ParsedBackendString) -> ta.Any:
        raise NotImplementedError


#


@dc.dataclass(frozen=True)
class ModelNameBackendStringPack:
    service_cls: str | ta.Collection[str]

    default_model_name: str

    _: dc.KW_ONLY

    model_name_aliases: ta.Mapping[str, str] | None = None

    @cached.property
    def model_name_alias_map(self) -> ta.Mapping[str, str]:
        if not (src := self.model_name_aliases):
            return {}

        dct: dict[str, str] = {}
        for ks in mut_toposort({k: {v} for k, v in src.items()}):
            for k in ks:
                dct[k] = dct.get(src.get(k, k), k)
        return dct

    @cached.property
    def root_model_names(self) -> frozenset[str]:
        return frozenset(self.model_name_alias_map.values())


class ModelNameBackendStringPackInstantiator(BackendStringInstantiator):
    def __init__(
            self,
            pack: ModelNameBackendStringPack,
    ) -> None:
        super().__init__()

        self._pack = pack

    def instantiate_backend_string(self, bs: ParsedBackendString) -> ta.Any:
        raise NotImplementedError
