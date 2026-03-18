# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
"""
Notes:
 - necessarily string-oriented
 - single file, as this is intended to be amalg'd and thus all included anyway

TODO:
 - ConfigDataMapper? to_map -> ConfigMap?
 - nginx ?
 - raw ?
"""
import abc
import collections.abc
import configparser
import dataclasses as dc
import json
import os.path
import typing as ta

from ..formats.ini.sections import IniSectionSettingsMap
from ..formats.ini.sections import extract_ini_sections
from ..formats.ini.sections import render_ini_sections
from ..formats.toml.parser import toml_loads
from ..formats.toml.writer import TomlWriter
from ..lite.abstract import Abstract
from ..lite.check import check
from ..lite.json import json_dumps_pretty
from .types import ConfigMap


T = ta.TypeVar('T')

ConfigDataT = ta.TypeVar('ConfigDataT', bound='ConfigData')
ObjConfigDataT = ta.TypeVar('ObjConfigDataT', bound='ObjConfigData')


##


@dc.dataclass(frozen=True)
class ConfigData(Abstract):
    @abc.abstractmethod
    def as_map(self) -> ConfigMap:
        raise NotImplementedError


#


class ConfigLoaderContext:
    pass


class ConfigFileLoader(Abstract, ta.Generic[ConfigDataT]):
    @property
    @abc.abstractmethod
    def data_cls(self) -> ta.Type[ConfigDataT]:
        raise NotImplementedError

    @property
    def file_exts(self) -> ta.Sequence[str]:
        return ()

    def match_file(self, n: str) -> bool:
        return '.' in n and n.split('.', maxsplit=1)[-1] in check.not_isinstance(self.file_exts, str)

    def find_file(self, p: str) -> ta.Optional[str]:
        hits: ta.List[str] = []
        for e in self.file_exts:
            cur = f'{p}.{e}'
            if os.path.exists(cur):
                check.state(os.path.isfile(cur))
                hits.append(cur)
        if hits:
            return check.single(hits)
        return None

    @abc.abstractmethod
    def load_file(self, p: str, ctx: ta.Optional[ConfigLoaderContext] = None) -> ConfigDataT:
        raise NotImplementedError


class ConfigLoader(ConfigFileLoader[ConfigDataT], Abstract, ta.Generic[ConfigDataT]):
    def load_file(self, p: str, ctx: ta.Optional[ConfigLoaderContext] = None) -> ConfigDataT:
        with open(p) as f:
            return self.load_str(f.read(), ctx)

    @abc.abstractmethod
    def load_str(self, s: str, ctx: ta.Optional[ConfigLoaderContext] = None) -> ConfigDataT:
        raise NotImplementedError


#


class ProxyConfigFileLoader(ConfigFileLoader[ConfigDataT]):
    def __init__(self, underlying: ta.Union[ConfigLoader[ConfigDataT], ta.Callable[[], ConfigLoader[ConfigDataT]]]) -> None:  # noqa
        super().__init__()

        self._underlying = underlying

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self._underlying!r})'

    @property
    def underlying(self) -> ta.Union[ConfigLoader[ConfigDataT], ta.Callable[[], ConfigLoader[ConfigDataT]]]:
        return self._underlying

    def get_underlying(self) -> ConfigLoader[ConfigDataT]:
        if callable(ul := self._underlying):
            ul = ul()
        return ul

    #

    @property
    def data_cls(self) -> ta.Type[ConfigDataT]:
        return self.get_underlying().data_cls

    @property
    def file_exts(self) -> ta.Sequence[str]:
        return self.get_underlying().file_exts

    def match_file(self, n: str) -> bool:
        return self.get_underlying().match_file(n)

    def find_file(self, p: str) -> ta.Optional[str]:
        return self.get_underlying().find_file(p)

    def load_file(self, p: str, ctx: ta.Optional[ConfigLoaderContext] = None) -> ConfigDataT:
        return self.get_underlying().load_file(p, ctx)


class ProxyConfigLoader(ProxyConfigFileLoader[ConfigDataT], ConfigLoader[ConfigDataT]):
    def load_str(self, s: str, ctx: ta.Optional[ConfigLoaderContext] = None) -> ConfigDataT:
        return self.get_underlying().load_str(s, ctx)


#


class ConfigRendererContext:
    pass


class ConfigRenderer(Abstract, ta.Generic[ConfigDataT]):
    @property
    @abc.abstractmethod
    def data_cls(self) -> ta.Type[ConfigDataT]:
        raise NotImplementedError

    def match_data(self, d: ConfigDataT) -> bool:
        return isinstance(d, self.data_cls)

    #

    @abc.abstractmethod
    def render(self, d: ConfigDataT, ctx: ta.Optional[ConfigRendererContext] = None) -> str:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class ObjConfigData(ConfigData, Abstract):
    obj: ta.Any

    def as_map(self) -> ConfigMap:
        return check.isinstance(self.obj, collections.abc.Mapping)


##


class LoadsConfigLoader(ConfigLoader[ObjConfigDataT], Abstract, ta.Generic[ObjConfigDataT]):
    @abc.abstractmethod
    def loads(self, s: str) -> ta.Any:
        raise NotImplementedError

    def load_str(self, s: str, ctx: ta.Optional[ConfigLoaderContext] = None) -> ObjConfigDataT:
        return self.data_cls(self.loads(s))


class DumpsConfigRenderer(ConfigRenderer[ObjConfigDataT], Abstract, ta.Generic[ObjConfigDataT]):
    @abc.abstractmethod
    def dumps(self, o: ta.Any) -> str:
        raise NotImplementedError

    def render(self, d: ObjConfigDataT, ctx: ta.Optional[ConfigRendererContext] = None) -> str:
        return self.dumps(d.obj)


##


@dc.dataclass(frozen=True)
class JsonConfigData(ObjConfigData):
    pass


class JsonConfigLoader(LoadsConfigLoader[JsonConfigData]):
    data_cls = JsonConfigData
    file_exts = ('json',)

    def loads(self, s: str) -> ta.Any:
        return json.loads(s)


class JsonConfigRenderer(DumpsConfigRenderer[JsonConfigData]):
    data_cls = JsonConfigData

    def dumps(self, o: ta.Any) -> str:
        return json_dumps_pretty(o)


##


@dc.dataclass(frozen=True)
class TomlConfigData(ObjConfigData):
    pass


class TomlConfigLoader(LoadsConfigLoader[TomlConfigData]):
    data_cls = TomlConfigData
    file_exts = ('toml',)

    def loads(self, s: str) -> ta.Any:
        return toml_loads(s)


class TomlConfigRenderer(DumpsConfigRenderer[TomlConfigData]):
    data_cls = TomlConfigData

    def dumps(self, o: ta.Any) -> str:
        return TomlWriter.write_str(o)


##


@dc.dataclass(frozen=True)
class YamlConfigData(ObjConfigData):
    pass


class YamlConfigBackend(Abstract):
    @abc.abstractmethod
    def loads(self, s: str) -> ta.Any:
        raise NotImplementedError

    @abc.abstractmethod
    def dumps(self, o: ta.Any) -> str:
        raise NotImplementedError


class PyyamlYamlConfigBackend(YamlConfigBackend):
    def loads(self, s: str) -> ta.Any:
        import yaml  # noqa

        return yaml.safe_load(s)

    def dumps(self, o: ta.Any) -> str:
        import yaml  # noqa

        return yaml.safe_dump(o)


DEFAULT_YAML_CONFIG_BACKEND = PyyamlYamlConfigBackend()


class YamlConfigLoader(LoadsConfigLoader[YamlConfigData]):
    data_cls = YamlConfigData
    file_exts = ('yaml', 'yml')
    backend: ta.Optional[YamlConfigBackend] = None

    def loads(self, s: str) -> ta.Any:
        return (self.backend or DEFAULT_YAML_CONFIG_BACKEND).loads(s)


class YamlConfigRenderer(DumpsConfigRenderer[YamlConfigData]):
    data_cls = YamlConfigData
    backend: ta.Optional[YamlConfigBackend] = None

    def dumps(self, o: ta.Any) -> str:
        return (self.backend or DEFAULT_YAML_CONFIG_BACKEND).dumps(o)


##


@dc.dataclass(frozen=True)
class IniConfigData(ConfigData):
    sections: IniSectionSettingsMap

    def as_map(self) -> ConfigMap:
        return self.sections


class IniConfigLoader(ConfigLoader[IniConfigData]):
    data_cls = IniConfigData
    file_exts = ('ini',)

    def load_str(self, s: str, ctx: ta.Optional[ConfigLoaderContext] = None) -> IniConfigData:
        cp = configparser.ConfigParser()
        cp.read_string(s)
        return IniConfigData(extract_ini_sections(cp))


class IniConfigRenderer(ConfigRenderer[IniConfigData]):
    data_cls = IniConfigData

    def render(self, d: IniConfigData, ctx: ta.Optional[ConfigRendererContext] = None) -> str:
        return render_ini_sections(d.sections)


##


DEFAULT_CONFIG_LOADERS: ta.Sequence[ConfigLoader] = [
    JsonConfigLoader(),
    TomlConfigLoader(),
    YamlConfigLoader(),
    IniConfigLoader(),
]

DEFAULT_CONFIG_LOADER: ConfigLoader = JsonConfigLoader()


#


@dc.dataclass(frozen=True)
class SwitchedConfigFileLoader(ConfigFileLoader[ConfigData]):
    loaders: ta.Sequence[ConfigLoader]
    default: ta.Optional[ConfigLoader] = None

    def __post_init__(self) -> None:
        seen: ta.Set[str] = set()
        for l in self.loaders:
            for e in l.file_exts:
                if e in seen:
                    raise ValueError(e)
                seen.add(e)

    @property
    def data_cls(self) -> ta.Type[ConfigData]:
        return ConfigData

    @property
    def file_exts(self) -> ta.Sequence[str]:
        return [e for l in self.loaders for e in l.file_exts]

    def load_file(self, p: str, ctx: ta.Optional[ConfigLoaderContext] = None) -> ConfigData:
        n = os.path.basename(p)

        for l in self.loaders:
            if l.match_file(n):
                return l.load_file(p, ctx)

        if (d := self.default) is not None:
            return d.load_file(p, ctx)

        raise NameError(n)


DEFAULT_CONFIG_FILE_LOADER = SwitchedConfigFileLoader(
    loaders=DEFAULT_CONFIG_LOADERS,
    default=DEFAULT_CONFIG_LOADER,
)


##


@dc.dataclass(frozen=True)
class SwitchedConfigRenderer(ConfigRenderer[ConfigData]):
    renderers: ta.Sequence[ConfigRenderer]

    @property
    def data_cls(self) -> ta.Type[ConfigData]:
        return ConfigData

    def render(self, d: ConfigData, ctx: ta.Optional[ConfigRendererContext] = None) -> str:
        for r in self.renderers:
            if r.match_data(d):
                return r.render(d, ctx)
        raise TypeError(d)


DEFAULT_CONFIG_RENDERERS: ta.Sequence[ConfigRenderer] = [
    JsonConfigRenderer(),
    TomlConfigRenderer(),
    YamlConfigRenderer(),
    IniConfigRenderer(),
]

DEFAULT_CONFIG_RENDERER = SwitchedConfigRenderer(DEFAULT_CONFIG_RENDERERS)
