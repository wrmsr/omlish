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


##


@dc.dataclass(frozen=True)
class ConfigData(Abstract):
    @abc.abstractmethod
    def as_map(self) -> ConfigMap:
        raise NotImplementedError


#


class ConfigLoader(Abstract, ta.Generic[ConfigDataT]):
    @property
    def file_exts(self) -> ta.Sequence[str]:
        return ()

    def match_file(self, n: str) -> bool:
        return '.' in n and n.split('.')[-1] in check.not_isinstance(self.file_exts, str)

    #

    def load_file(self, p: str) -> ConfigDataT:
        with open(p) as f:
            return self.load_str(f.read())

    @abc.abstractmethod
    def load_str(self, s: str) -> ConfigDataT:
        raise NotImplementedError


#


class ConfigRenderer(Abstract, ta.Generic[ConfigDataT]):
    @property
    @abc.abstractmethod
    def data_cls(self) -> ta.Type[ConfigDataT]:
        raise NotImplementedError

    def match_data(self, d: ConfigDataT) -> bool:
        return isinstance(d, self.data_cls)

    #

    @abc.abstractmethod
    def render(self, d: ConfigDataT) -> str:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class ObjConfigData(ConfigData, Abstract):
    obj: ta.Any

    def as_map(self) -> ConfigMap:
        return check.isinstance(self.obj, collections.abc.Mapping)


##


@dc.dataclass(frozen=True)
class JsonConfigData(ObjConfigData):
    pass


class JsonConfigLoader(ConfigLoader[JsonConfigData]):
    file_exts = ('json',)

    def load_str(self, s: str) -> JsonConfigData:
        return JsonConfigData(json.loads(s))


class JsonConfigRenderer(ConfigRenderer[JsonConfigData]):
    data_cls = JsonConfigData

    def render(self, d: JsonConfigData) -> str:
        return json_dumps_pretty(d.obj)


##


@dc.dataclass(frozen=True)
class TomlConfigData(ObjConfigData):
    pass


class TomlConfigLoader(ConfigLoader[TomlConfigData]):
    file_exts = ('toml',)

    def load_str(self, s: str) -> TomlConfigData:
        return TomlConfigData(toml_loads(s))


class TomlConfigRenderer(ConfigRenderer[TomlConfigData]):
    data_cls = TomlConfigData

    def render(self, d: TomlConfigData) -> str:
        return TomlWriter.write_str(d.obj)


##


@dc.dataclass(frozen=True)
class YamlConfigData(ObjConfigData):
    pass


class YamlConfigLoader(ConfigLoader[YamlConfigData]):
    file_exts = ('yaml', 'yml')

    def load_str(self, s: str) -> YamlConfigData:
        import yaml  # noqa

        return YamlConfigData(yaml.safe_load(s))


class YamlConfigRenderer(ConfigRenderer[YamlConfigData]):
    data_cls = YamlConfigData

    def render(self, d: YamlConfigData) -> str:
        import yaml  # noqa

        return yaml.safe_dump(d.obj)


##


@dc.dataclass(frozen=True)
class IniConfigData(ConfigData):
    sections: IniSectionSettingsMap

    def as_map(self) -> ConfigMap:
        return self.sections


class IniConfigLoader(ConfigLoader[IniConfigData]):
    file_exts = ('ini',)

    def load_str(self, s: str) -> IniConfigData:
        cp = configparser.ConfigParser()
        cp.read_string(s)
        return IniConfigData(extract_ini_sections(cp))


class IniConfigRenderer(ConfigRenderer[IniConfigData]):
    data_cls = IniConfigData

    def render(self, d: IniConfigData) -> str:
        return render_ini_sections(d.sections)


##


@dc.dataclass(frozen=True)
class SwitchedConfigFileLoader:
    loaders: ta.Sequence[ConfigLoader]
    default: ta.Optional[ConfigLoader] = None

    def load_file(self, p: str) -> ConfigData:
        n = os.path.basename(p)

        for l in self.loaders:
            if l.match_file(n):
                return l.load_file(p)

        if (d := self.default) is not None:
            return d.load_file(p)

        raise NameError(n)


DEFAULT_CONFIG_LOADERS: ta.Sequence[ConfigLoader] = [
    JsonConfigLoader(),
    TomlConfigLoader(),
    YamlConfigLoader(),
    IniConfigLoader(),
]

DEFAULT_CONFIG_LOADER: ConfigLoader = JsonConfigLoader()

DEFAULT_CONFIG_FILE_LOADER = SwitchedConfigFileLoader(
    loaders=DEFAULT_CONFIG_LOADERS,
    default=DEFAULT_CONFIG_LOADER,
)


##


@dc.dataclass(frozen=True)
class SwitchedConfigRenderer:
    renderers: ta.Sequence[ConfigRenderer]

    def render(self, d: ConfigData) -> str:
        for r in self.renderers:
            if r.match_data(d):
                return r.render(d)
        raise TypeError(d)


DEFAULT_CONFIG_RENDERERS: ta.Sequence[ConfigRenderer] = [
    JsonConfigRenderer(),
    TomlConfigRenderer(),
    YamlConfigRenderer(),
    IniConfigRenderer(),
]

DEFAULT_CONFIG_RENDERER = SwitchedConfigRenderer(DEFAULT_CONFIG_RENDERERS)
