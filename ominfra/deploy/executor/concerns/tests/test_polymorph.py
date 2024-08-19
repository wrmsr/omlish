# ruff: noqa: UP006
import abc
import dataclasses as dc
import json
import typing as ta

from omlish.lite.json import json_dumps_compact
from omlish.lite.marshal import marshal_obj
from omlish.lite.marshal import unmarshal_obj


##


ConcernConfigT = ta.TypeVar('ConcernConfigT', bound='Concern.Config')


class Concern(abc.ABC, ta.Generic[ConcernConfigT]):
    @dc.dataclass(frozen=True)
    class Config(abc.ABC):  # noqa
        pass

    def __init__(self, config: ConcernConfigT) -> None:
        super().__init__()
        self._config = config


##


class RepoConcern(Concern['RepoConcern.Config']):
    @dc.dataclass(frozen=True)
    class Config(Concern.Config):
        url: str


##


class VenvConcern(Concern['VenvConcern.Config']):
    @dc.dataclass(frozen=True)
    class Config(Concern.Config):
        interp_version: str


##


CONCERN_CLS_BY_CONFIG_CLS: ta.Mapping[ta.Type[Concern.Config], ta.Type[Concern]] = {
    cls.Config: cls
    for cls in Concern.__subclasses__()
}


class Deploy:
    @dc.dataclass(frozen=True)
    class Config:
        concerns: ta.List[Concern.Config]

    def __init__(self, config: Config) -> None:
        super().__init__()
        self._config = config

        self._concerns = [CONCERN_CLS_BY_CONFIG_CLS[type(c)](c) for c in config.concerns]
        self._concerns_by_cls: ta.Dict[ta.Type[Concern], Concern] = {}
        for c in self._concerns:
            if type(c) in self._concerns_by_cls:
                raise TypeError(f'Duplicate concern type: {c}')
            self._concerns_by_cls[type(c)] = c


##


def test_polymorph():
    dcfg = Deploy.Config(
        concerns=[
            RepoConcern.Config(
                url='https://github.com/wrmsr/omlish',
            ),
            VenvConcern.Config(
                interp_version='3.12.5',
            ),
        ],
    )
    print(dcfg)

    jdcfg = json_dumps_compact(marshal_obj(dcfg))
    print(jdcfg)

    dcfg2: Deploy.Config = unmarshal_obj(json.loads(jdcfg), Deploy.Config)
    print(dcfg2)

    d = Deploy(dcfg2)
    print(d)
